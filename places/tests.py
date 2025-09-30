from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Place
from django.contrib.auth import get_user_model

User = get_user_model()

class PlaceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.force_authenticate(self.user)
        self.place = Place.objects.create(
            name='Test Mess', type='food', sub_type='mess', address='Test Address',
            latitude=12.34, longitude=56.78, price_level='economical', added_by=self.user, is_approved=True
        )

    def test_add_place(self):
        data = {
            'name': 'New Place', 'type': 'stay', 'sub_type': 'pg', 'address': 'New Addr',
            'latitude': 10.0, 'longitude': 20.0, 'price_level': 'average'
        }
        response = self.client.post('/places/add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_recommendations(self):
        response = self.client.get('/places/recommendations/?location=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_filter_search(self):
        response = self.client.get('/places/?type=food&search=mess&min_rating=0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail(self):
        response = self.client.get(f'/places/{self.place.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reviews', response.data)

    def test_favorite(self):
        response = self.client.post(f'/places/{self.place.pk}/favorite/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.place.favorites.filter(id=self.user.id).exists())

    def test_report(self):
        response = self.client.post(f'/places/{self.place.pk}/report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.place.refresh_from_db()
        self.assertTrue(self.place.reported)