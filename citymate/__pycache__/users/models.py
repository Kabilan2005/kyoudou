from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField( max_length=10,choices=ROLE_CHOICES,default='user')