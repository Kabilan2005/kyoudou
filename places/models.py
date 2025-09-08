from django.db import models
from django.conf import settings

# Create your models here.
class Place(models.Model):
    PLACE_TYPE_CHOICES = (
        ('accomodation','Hostel/PG/Room'),
        ('hotel','Hotel'),
        ('mess','Mess'),
        ('bakery','Bakery'),
        ('stall','Food Stall'),
        ('stationery','Stationery'),
        ('Grocery','grocery')
    )

    PRICE_TIER_CHOICES =(
        ('economy','Economical'),
        ('average','Average'),
        ('premium','Premium')
    )

    name = models.CharField(_(""), max_length=50)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=50)
    place_type = models.CharField(max_length=20,choices=PLACE_TYPE_CHOICES,default='Food')
    price_tier = models.CharField(_(""), max_length=50,choices=PRICE_TIER_CHOICES,default='Economical')
    is_verified = models.BooleanField(default=False)

    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(""), on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_At = models.DateTimeField(auto_now=True)

    def __str__(own):
        return own.name