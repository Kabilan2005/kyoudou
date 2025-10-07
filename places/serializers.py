from rest_framework import serializers
from .models import Place
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class PlaceSerializer(serializers.ModelSerializer):
    added_by = serializers.StringRelatedField()  # Show username
    is_favorited = serializers.SerializerMethodField()  # Check if favorited by current user

    class Meta:
        model = Place
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorites.filter(id=user.id).exists()
        return False

class PlaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['name', 'type', 'sub_type', 'address', 'latitude', 'longitude', 'price_level', 'description', 'contact_info', 'photos']

    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)