from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from ratelimit import limits, RateLimitException
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from .models import User, OTP
from .serializers import (
    UserSerializer,
    SignupSerializer,
    VerificationSerializer,
    ProfileUpdateSerializer,
    PasswordResetSerializer,
)
import logging

logger = logging.getLogger(__name__)
SIXTY_SECONDS = 60
FIVE_CALLS = 5


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response(
                {
                    "message": "Welcome to home!",
                    "user": UserSerializer(request.user).data,
                }
            )
        else:
            return Response(
                {"message": "Please sign up or log in."},
                status=status.HTTP_302_FOUND,
            )


class SignupView(APIView):
    permission_classes = [AllowAny]

    @limits(calls=FIVE_CALLS, period=SIXTY_SECONDS)
    def post(self, request):
        try:
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data

                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=data.get("email") or data.get("phone_number"),
                            email=data.get("email"),
                            phone_number=data.get("phone_number"),
                            age=data.get("age"),
                            preferred_city=data.get("preferred_city"),
                            user_type=data.get("user_type"),
                        )
                        if data.get("password"):
                            user.set_password(data["password"])
                            user.save()
                except Exception as e:
                    logger.error(f"User creation failed: {str(e)}")
                    return Response(
                        {"error": "User creation failed — maybe already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                try:
                    if data.get("email"):
                        self.send_email_otp(user)
                    elif data.get("phone_number"):
                        self.send_phone_otp(user)
                except Exception as e:
                    logger.error(f"OTP sending failed: {str(e)}")
                    return Response(
                        {"error": "Failed to send OTP. Try again later."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                return Response(
                    {"message": "User created. Verify OTP."},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RateLimitException:
            return Response(
                {"error": "Rate limit exceeded"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return Response(
                {"error": "Internal error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def send_email_otp(self, user):
        otp = OTP.objects.create(user=user, type="email")
        send_mail(
            "Your OTP Code",
            f"Your verification code is {otp.code}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    def send_phone_otp(self, user):
        otp = OTP.objects.create(user=user, type="phone")
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Your verification code is {otp.code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number,
        )


class VerificationView(APIView):
    permission_classes = [AllowAny]

    @limits(calls=FIVE_CALLS, period=SIXTY_SECONDS)
    def post(self, request):
        try:
            serializer = VerificationSerializer(data=request.data)
            if serializer.is_valid():
                code = serializer.validated_data["code"]
                otp = OTP.objects.filter(code=code).first()

                if otp and otp.is_valid():
                    user = otp.user

                    if otp.type == "email":
                        user.email_verified = True
                    elif otp.type == "phone":
                        user.phone_verified = True

                    user.is_verified = user.email_verified or user.phone_verified
                    user.save()
                    otp.delete()

                    login(request, user)
                    refresh = RefreshToken.for_user(user)

                    return Response({
                        "message": "Verified successfully",
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    })

                return Response({"error": "Invalid or expired OTP"}, status=400)
            return Response(serializer.errors, status=400)
        except RateLimitException:
            return Response({"error": "Rate limit exceeded"}, status=429)
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return Response({"error": "Internal error"}, status=500)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @limits(calls=FIVE_CALLS, period=SIXTY_SECONDS)
    def post(self, request):
        try:
            serializer = PasswordResetSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                email_or_phone = data["email_or_phone"]

                user = (
                    User.objects.filter(email=email_or_phone).first()
                    or User.objects.filter(phone_number=email_or_phone).first()
                )
                if not user:
                    return Response({"error": "User not found"}, status=404)

                # Step 1: Send OTP if no code yet
                if "code" not in data:
                    try:
                        if "@" in email_or_phone:
                            SignupView().send_email_otp(user)
                        else:
                            SignupView().send_phone_otp(user)
                    except Exception as e:
                        logger.error(f"OTP send error: {e}")
                        return Response({"error": "Failed to send OTP"}, status=500)

                    return Response({"message": "Reset OTP sent"})

                # Step 2: Verify OTP and reset password
                otp = OTP.objects.filter(user=user, code=data["code"]).first()
                if otp and otp.is_valid():
                    user.set_password(data.get("new_password"))
                    user.save() 
                    otp.delete()
                    return Response({"message": "Password reset successfully"})
                return Response({"error": "Invalid or expired OTP"}, status=400)

            return Response(serializer.errors, status=400)

        except RateLimitException:
            return Response({"error": "Rate limit exceeded"}, status=429)
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response({"error": "Internal error"}, status=500)
