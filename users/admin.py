from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTP

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'age', 'is_verified', 'user_type')
    list_filter = ('is_verified', 'user_type', 'email_verified', 'phone_verified')
    search_fields = ('username', 'email', 'phone_number')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'age', 'preferred_city', 'user_type', 'email_verified', 'phone_verified')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(OTP)