from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'age', 'preferred_city', 'user_type', 'is_verified']

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)  # For password fallback
    age = serializers.IntegerField(required=False)
    preferred_city = serializers.CharField(required=False)
    user_type = serializers.ChoiceField(choices=[('student', 'Student'), ('working', 'Working')], required=False)

    def validate(self, data):
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError("Provide either email or phone number.")
        return data

class VerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['age', 'preferred_city', 'user_type']

class PasswordResetSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    code = serializers.CharField(max_length=6, required=False)
    new_password = serializers.CharField(write_only=True, required=False)