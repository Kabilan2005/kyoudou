from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from geopy.distance import distance as geopy_distance

User = get_user_model()

class Place(models.Model):
    TYPE_CHOICES = (
        ('food', 'Food'),
        ('stay', 'Stay'),
    )
    SUB_TYPE_CHOICES = (
        ('mess', 'Mess'),
        ('bakery', 'Bakery'),
        ('stall', 'Stall'),
        ('hotel', 'Hotel'),
        ('pg', 'PG'),
        ('hostel', 'Hostel'),
        ('rental', 'Rental'),
    )
    PRICE_LEVEL_CHOICES = (
        ('economical', 'Economical'),
        ('average', 'Average'),
        ('premium', 'Premium'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    sub_type = models.CharField(max_length=10, choices=SUB_TYPE_CHOICES)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    price_level = models.CharField(max_length=10, choices=PRICE_LEVEL_CHOICES)
    description = models.TextField(blank=True)
    contact_info = models.CharField(max_length=255, blank=True)
    photos = models.JSONField(default=list, blank=True)  
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_places')
    is_approved = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0.0)
    favorites = models.ManyToManyField(User, related_name='favorite_places', blank=True)
    reported = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.sub_type})"

    def calculate_distance(self, user_lat, user_lon):
        return geopy_distance((self.latitude, self.longitude), (user_lat, user_lon)).km

# Signal to update average_rating when a review is saved (assumes reviews app has Review model)
@receiver(post_save, sender='reviews.Review')  
def update_place_rating(sender, instance, **kwargs):
    place = instance.place
    place.average_rating = place.reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
    place.save(update_fields=['average_rating'])