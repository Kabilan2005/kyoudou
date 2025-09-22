from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  # Include users URLs at root
    path('places/', include('places.urls')),  # Assuming you have these
    path('reviews/', include('reviews.urls')),
]