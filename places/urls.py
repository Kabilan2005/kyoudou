from django.urls import path
from .views import RecommendationView, PlaceListView, PlaceDetailView, AddPlaceView, FavoritePlaceView, ReportPlaceView

urlpatterns = [
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('', PlaceListView.as_view(), name='place_list'),
    path('<int:pk>/', PlaceDetailView.as_view(), name='place_detail'),
    path('add/', AddPlaceView.as_view(), name='add_place'),
    path('<int:pk>/favorite/', FavoritePlaceView.as_view(), name='favorite_place'),
    path('<int:pk>/report/', ReportPlaceView.as_view(), name='report_place'),
]