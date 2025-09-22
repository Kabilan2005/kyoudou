from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, OTP
from .views import SignupView

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {'email': 'test@example.com', 'password': 'testpass', 'age': 25}

    def test_signup_and_verify(self):
        # Test signup
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Simulate OTP (in test, we can't send real email)
        user = User.objects.get(email='test@example.com')
        otp = OTP.objects.create(user=user, code='123456', type='email')
        response = self.client.post(reverse('verify'), {'code': '123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_login(self):
        user = User.objects.create_user(email='login@example.com', password='pass')
        response = self.client.post(reverse('login'), {'username': 'login@example.com', 'password': 'pass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile_update(self):
        user = User.objects.create_user(email='profile@example.com', password='pass')
        self.client.force_authenticate(user)
        response = self.client.put(reverse('profile'), {'age': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.age, 30)

    def test_password_reset(self):
        user = User.objects.create_user(email='reset@example.com', password='oldpass')
        # Step 1: Request OTP
        response = self.client.post(reverse('password_reset'), {'email_or_phone': 'reset@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Simulate OTP
        otp = OTP.objects.create(user=user, code='654321', type='email')
        # Step 2: Reset
        response = self.client.post(reverse('password_reset'), {
            'email_or_phone': 'reset@example.com',
            'code': '654321',
            'new_password': 'newpass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpass'))

    def test_rate_limit(self):
        for _ in range(6):  # Exceed 5
            self.client.post(reverse('signup'), self.user_data)
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)