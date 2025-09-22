from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
from ratelimit import limits, RateLimitException
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.account.utils import complete_social_login
from django.http import HttpResponseRedirect
from .models import User, OTP
from .serializers import UserSerializer, SignupSerializer, VerificationSerializer, ProfileUpdateSerializer, PasswordResetSerializer
import logging

logger = logging.getLogger(__name__)

# Rate limit: 5 requests per minute for sensitive views
SIXTY_SECONDS = 60
FIVE_CALLS = 5

class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({"message": "Welcome to home!", "user": UserSerializer(request.user).data})
        else:
            return Response({"message": "Please sign up or log in."}, status=status.HTTP_302_FOUND)  # Simulate redirect to signup

class SignupView(APIView):
    permission_classes = [AllowAny]

    @limits(calls=FIVE_CALLS, period=SIXTY_SECONDS)
    def post(self, request):
        try:
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                user_kwargs = {
                    'username': data.get('email') or data.get('phone_number'),
                    'email': data.get('email'),
                    'phone_number': data.get('phone_number'),
                    'age': data.get('age'),
                    'preferred_city': data.get('preferred_city'),
                    'user_type': data.get('user_type'),
                }
                user = User.objects.create_user(**user_kwargs)
                if data.get('password'):
                    user.set_password(data['password'])
                    user.save()
                # Send verification
                if data.get('email'):
                    self.send_email_otp(user)
                elif data.get('phone_number'):
                    self.send_phone_otp(user)
                return Response({"message": "User created. Verify OTP."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RateLimitException:
            return Response({"error": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return Response({"error": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_otp(self, user):
        otp = OTP.objects.create(user=user, type='email')
        send_mail(
            'Your OTP Code',
            f'Your verification code is {otp.code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    def send_phone_otp(self, user):
        otp = OTP.objects.create(user=user, type='phone')
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f'Your verification code is {otp.code}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )

class VerificationView(APIView):
    permission_classes = [AllowAny]

    @limits(calls=FIVE_CALLS, period=SIXTY_SECONDS)
    def post(self, request):
        try:
            serializer = VerificationSerializer(data=request.data)
            if serializer.is_valid():
                code = serializer.validated_data['code']
                otp = OTP.objects.filter(code=code).first()
                if otp and otp.is_valid():
                    user = otp.user
                    if otp.type == 'email':
                        user.email_verified = True
                    elif otp.type == 'phone':
                        user.phone_verified = True
                    user.is_verified = user.email_verified or user.phone_verified
                    user.save()
                    otp.delete()  # One-time use
                    # Log in user and generate tokens for persistent session
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "message": "Verified successfully",
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    })
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RateLimitException:
            return Response({"error": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return Response({"error": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Handle Google callback (allauth handles most, but simulate redirect)
        adapter = GoogleOAuth2Adapter(request)
        token = request.GET.get('code')  # From Google redirect
        # Complete login (allauth logic)
        social_login = complete_social_login(request, adapter, token)
        if social_login:
            user = social_login.user
            user.is_verified = True  # Google verifies
            user.save()
            login(request, user)
            return HttpResponseRedirect('/')  # To home
        return Response({"error": "Google login failed"}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
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
                email_or_phone = data['email_or_phone']
                user = User.objects.filter(email=email_or_phone).first() or User.objects.filter(phone_number=email_or_phone).first()
                if not user:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                
                if 'code' not in data:  # Step 1: Send reset OTP
                    if '@' in email_or_phone:
                        SignupView().send_email_otp(user)
                    else:
                        SignupView().send_phone_otp(user)
                    return Response({"message": "Reset OTP sent"})
                
                # Step 2: Verify code and reset password
                code = data['code']
                new_password = data.get('new_password')
                otp = OTP.objects.filter(user=user, code=code).first()
                if otp and otp.is_valid():
                    user.set_password(new_password)
                    user.save()
                    otp.delete()
                    return Response({"message": "Password reset successfully"})
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RateLimitException:
            return Response({"error": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response({"error": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)