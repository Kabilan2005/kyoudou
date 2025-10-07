from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from geopy.distance import distance as geopy_distance

User = get_user_model()

class Place(models.Model):
    TYPE_CHOICES = (('food', 'Food'), ('stay', 'Stay'))
    SUB_TYPE_CHOICES = (('mess', 'Mess'), ('bakery', 'Bakery'), ('stall', 'Stall'), ('hotel', 'Hotel'), ('pg', 'PG'), ('hostel', 'Hostel'), ('rental', 'Rental'))
    PRICE_LEVEL_CHOICES = (('economical', 'Economical'), ('average', 'Average'), ('premium', 'Premium'))

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    sub_type = models.CharField(max_length=10, choices=SUB_TYPE_CHOICES)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    price_level = models.CharField(max_length=10, choices=PRICE_LEVEL_CHOICES)
    description = models.TextField(blank=True)
    contact_info = models.CharField(max_length=255, blank=True)
    
    # CHANGED: Switched from JSONField to ImageField for a single photo
    # As of now single photo is allowed for Simplicity
    photo = models.ImageField(upload_to='place_photos/', null=True, blank=True)
    
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags, e.g., cozy, late-night, wifi")

    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_places')
    is_approved = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0.0)
    favorites = models.ManyToManyField(User, related_name='favorite_places', blank=True)
    reported = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.sub_type})"

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def calculate_distance(self, user_lat, user_lon):
        if self.latitude and self.longitude and user_lat and user_lon:
            return geopy_distance((self.latitude, self.longitude), (user_lat, user_lon)).km
        return None

# Signal to update average_rating when a review is saved
@receiver(post_save, sender='reviews.Review')
def update_place_rating(sender, instance, **kwargs):
    place = instance.place
    average = place.reviews.aggregate(Avg('rating'))['rating__avg']
    place.average_rating = average or 0.0
    place.save(update_fields=['average_rating'])