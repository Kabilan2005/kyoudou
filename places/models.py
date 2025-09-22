from django.db import models
from django.conf import settings


class Place(models.Model):
    PLACE_TYPE_CHOICES = (
        ('accomodation', 'Hostel/PG/Room'),
        ('hotel', 'Hotel'),
        ('mess', 'Mess'),
        ('bakery', 'Bakery'),
        ('stall', 'Food Stall'),
        ('stationery', 'Stationery'),
        ('grocery', 'Grocery'),  
    )

    PRICE_TIER_CHOICES = (
        ('economy', 'Economical'),
        ('average', 'Average'),
        ('premium', 'Premium'),
    )

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=50)
    place_type = models.CharField(
        max_length=20, choices=PLACE_TYPE_CHOICES, default='accomodation'
    )
    price_tier = models.CharField(
        max_length=20, choices=PRICE_TIER_CHOICES, default='economy'
    )
    is_verified = models.BooleanField(default=False)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Added by",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
