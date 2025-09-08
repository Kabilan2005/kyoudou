from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    user_ID = models.AutoField(_(""))
    role = models.CharField(_(""), max_length=10,choices=ROLE_CHOICES,default='user')