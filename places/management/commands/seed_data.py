import random
from django.core.management.base import BaseCommand
from places.models import Place
from reviews.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with a rich set of dummy data for places and reviews.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding process...'))

        # --- User Setup ---
        users = []
        for i in range(3):
            username = f'user{i+1}'
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'user{i+1}@example.com'})
            if created:
                user.set_password('password')
                user.save()
            users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'Ensured {len(users)} dummy users exist.'))
        owner_user = users[0]

        # --- Clear Existing Data ---
        Review.objects.all().delete()
        Place.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing place and review data.'))

        # --- Dummy Data Definitions ---
        places_data = [
            # Food
            {'name': 'Annapoorna Gowrishankar', 'type': 'food', 'sub_type': 'mess', 'address': 'Peelamedu, Hope College, Coimbatore', 'lat': 11.0315, 'lon': 77.0160, 'price': 'average', 'tags': 'south indian, vegetarian, family', 'photo_url': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1974'},
            {'name': 'Sree Subbu Mess', 'type': 'food', 'sub_type': 'mess', 'address': 'Near CIT Campus, Civil Aerodrome Post, Coimbatore', 'lat': 11.0275, 'lon': 77.0235, 'price': 'economical', 'tags': 'chettinad, non-veg, students', 'photo_url': 'https://images.unsplash.com/photo-1552566626-52f8b828add9?q=80&w=2070'},
            {'name': 'The French Door', 'type': 'food', 'sub_type': 'bakery', 'address': 'R S Puram West, Coimbatore', 'lat': 11.0055, 'lon': 76.9558, 'price': 'premium', 'tags': 'cafe, dessert, european, romantic', 'photo_url': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?q=80&w=2047'},
            {'name': 'KR Bakes', 'type': 'food', 'sub_type': 'bakery', 'address': 'Avinashi Road, Near CIT, Coimbatore', 'lat': 11.0250, 'lon': 77.0230, 'price': 'economical', 'tags': 'snacks, bakery, quick bites', 'photo_url': 'https://images.unsplash.com/photo-1563502299833-258abbc6522a?q=80&w=1974'},
            {'name': 'Bird on Tree', 'type': 'food', 'sub_type': 'mess', 'address': 'Race Course, Coimbatore', 'lat': 11.0027, 'lon': 76.9796, 'price': 'premium', 'tags': 'continental, fine dining, rooftop', 'photo_url': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?q=80&w=2070'},
            
            # Stay
            {'name': 'CIT Boys Hostel', 'type': 'stay', 'sub_type': 'hostel', 'address': 'CIT Campus, Coimbatore', 'lat': 11.0270, 'lon': 77.0225, 'price': 'economical', 'tags': 'students, on-campus, budget', 'photo_url': 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?q=80&w=2070'},
            {'name': 'Fairfield by Marriott', 'type': 'stay', 'sub_type': 'hotel', 'address': 'Avinashi Road, near Airport, Coimbatore', 'lat': 11.0300, 'lon': 77.0400, 'price': 'premium', 'tags': 'luxury, business, airport hotel', 'photo_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=2070'},
            {'name': 'Sri Krishna PG for Gents', 'type': 'stay', 'sub_type': 'pg', 'address': 'Hope College, Peelamedu, Coimbatore', 'lat': 11.0320, 'lon': 77.0175, 'price': 'average', 'tags': 'students, working professionals, affordable', 'photo_url': 'https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80&w=1974'},
            {'name': 'The Residency Towers', 'type': 'stay', 'sub_type': 'hotel', 'address': 'Avinashi Road, Press Colony, Coimbatore', 'lat': 11.0163, 'lon': 76.9936, 'price': 'premium', 'tags': '5-star, luxury, rooftop pool', 'photo_url': 'https://images.unsplash.com/photo-1542314831-068cd1dbb5eb?q=80&w=2070'},
            {'name': 'Le Meridien', 'type': 'stay', 'sub_type': 'hotel', 'address': 'Neelambur, Coimbatore', 'lat': 11.0664, 'lon': 77.0853, 'price': 'premium', 'tags': 'luxury, spa, modern', 'photo_url': 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?q=80&w=1949'},
        ]
        
        created_places = []
        for place_data in places_data:
            # We are now saving the URL string to the 'photo' field
            place = Place.objects.create(
                name=place_data['name'],
                type=place_data['type'],
                sub_type=place_data['sub_type'],
                address=place_data['address'],
                latitude=place_data['lat'],
                longitude=place_data['lon'],
                price_level=place_data['price'],
                description=f"A popular spot in Coimbatore. Known for its {'great food' if place_data['type'] == 'food' else 'comfortable stay'}.",
                tags=place_data['tags'],
                photo=place_data['photo_url'], # Save the URL here
                is_approved=True,
                average_rating=round(random.uniform(3.5, 5.0), 1),
                added_by=owner_user
            )
            created_places.append(place)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {len(created_places)} places.'))

        # Dummy Reviews (code remains the same)
        # ... (rest of the review creation code is correct)

            # --- Dummy Reviews ---
        review_comments = [
            "Absolutely fantastic! A must-visit.",
            "Good, but could be better. The service was a bit slow.",
            "An average experience. Nothing too special.",
            "Loved the ambiance and the quality. Will definitely come back.",
            "Overpriced for what it is. I've had better."
        ]
            
        reviews_to_create = []
        for place in created_places:
                # Add 1 to 3 reviews for each place
            for _ in range(random.randint(1, 3)):
                review = Review(
                    place=place,
                    user=random.choice(users),
                    rating=random.randint(3, 5),
                    comment=random.choice(review_comments)
                )
                reviews_to_create.append(review)
            
        Review.objects.bulk_create(reviews_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully added {len(reviews_to_create)} reviews.'))
        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))