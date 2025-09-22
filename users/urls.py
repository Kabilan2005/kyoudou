from django.urls import path, include
from .views import HomeView, SignupView, VerificationView, LoginView, GoogleLoginView, ProfileView, PasswordResetView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify/', VerificationView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    # Include allauth URLs for Google init
    path('accounts/', include('allauth.urls')),
]