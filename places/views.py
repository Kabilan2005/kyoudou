from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.core.cache import cache
from ratelimit import limits
from .models import Place
from .serializers import PlaceSerializer, PlaceCreateSerializer
from reviews.models import Review  # Assume reviews app has Review model

SIXTY_SECONDS = 60
FIVE_CALLS = 5

class RecommendationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        location = request.query_params.get('location')  # e.g., 'Mumbai'
        lat = request.query_params.get('lat')  # Optional lat/lon for precise
        lon = request.query_params.get('lon')
        cache_key = f"recommendations_{location}_{lat}_{lon}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        queryset = Place.objects.filter(is_approved=True)
        if location:
            queryset = queryset.filter(address__icontains=location)
        if lat and lon:
            queryset = queryset.annotate(
                distance=Value(0)  # Placeholder; calculate in Python for simplicity
            ).order_by('distance')  # Sort by distance in view
            places = [p for p in queryset if (dist := p.calculate_distance(float(lat), float(lon))) < 10]  # Within 10km
            places.sort(key=lambda p: p.calculate_distance(float(lat), float(lon)))
        else:
            places = queryset.order_by('-average_rating')[:10]  # Top 10 by rating

        serializer = PlaceSerializer(places, many=True, context={'request': request})
        data = serializer.data
        cache.set(cache_key, data, timeout=300)  # Cache 5 min
        return Response(data)

class PlaceListView(APIView):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'sub_type', 'price_level']
    search_fields = ['name', 'description', 'address']
    ordering_fields = ['average_rating', 'name']

    def get(self, request):
        queryset = Place.objects.filter(is_approved=True)
        # Custom filters/search
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=min_rating)
        # Full-text search example
        search = request.query_params.get('search')
        if search:
            queryset = queryset.annotate(search=Concat('name', Value(' '), 'description')).filter(search__icontains=search)

        # Apply filters from backends
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        serializer = PlaceSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class PlaceDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            place = Place.objects.get(pk=pk, is_approved=True)
            serializer = PlaceSerializer(place, context={'request': request})
            data = serializer.data
            # Add reviews (from reviews app)
            reviews = Review.objects.filter(place=place)
            data['reviews'] = [{'rating': r.rating, 'text': r.text, 'user': r.user.username} for r in reviews]
            # Similar places
            similar = Place.objects.filter(type=place.type, price_level=place.price_level).exclude(pk=pk)[:5]
            data['similar'] = PlaceSerializer(similar, many=True, context={'request': request}).data
            return Response(data)
        except Place.DoesNotExist:
            return Response({"error": "Place not found"}, status=status.HTTP_404_NOT_FOUND)

class AddPlaceView(APIView):
    permission_classes = [IsAuthenticated]

    @limits(calls=FIVE_CALLS, period=SIXTY_SECONDS)
    def post(self, request):
        serializer = PlaceCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FavoritePlaceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            place = Place.objects.get(pk=pk)
            place.favorites.add(request.user)
            return Response({"message": "Favorited"})
        except Place.DoesNotExist:
            return Response({"error": "Place not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            place = Place.objects.get(pk=pk)
            place.favorites.remove(request.user)
            return Response({"message": "Unfavorited"})
        except Place.DoesNotExist:
            return Response({"error": "Place not found"}, status=status.HTTP_404_NOT_FOUND)

class ReportPlaceView(APIView):
    permission_classes = [IsAuthenticated]

    @limits(calls=FIVE_CALLS, period=SIXTY_SECONDS)
    def post(self, request, pk):
        try:
            place = Place.objects.get(pk=pk)
            place.reported = True
            place.save()
            return Response({"message": "Reported"})
        except Place.DoesNotExist:
            return Response({"error": "Place not found"}, status=status.HTTP_404_NOT_FOUND)