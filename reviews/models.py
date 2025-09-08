from django.db import models
from django.conf import settings 
from django.models import Place
 
# Create your models here.
class Review():
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    place = models.ForeignKey(Place,on_delete=models.CASCADE,related_name="reviews")
    rating = models.PositiveSmallIntegerField(default=3)
    comment = models.TextField(blank=True)

    crated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review on {self.place.name}"