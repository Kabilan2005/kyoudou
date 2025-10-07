from django.urls import path
from .views import HomeView, SearchView, AddPlaceView, AddReviewView, PlaceDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),
    path('add-place/', AddPlaceView.as_view(), name='add_place'),
    path('add-review/', AddReviewView.as_view(), name='add_review'),
    path('<int:pk>/', PlaceDetailView.as_view(), name='place_detail'),
]