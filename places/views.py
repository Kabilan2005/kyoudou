from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Place
from .forms import AddPlaceForm
from reviews.forms import AddReviewForm, ReviewFormForDetailPage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
import os
from django.conf import settings
from uuid import uuid4
from django.contrib import messages

class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        trending_places = Place.objects.filter(is_approved=True).order_by('-average_rating')[:10]
        nearby_places = Place.objects.filter(is_approved=True).order_by('?')[:10]
        recommendations = Place.objects.filter(is_approved=True, type='food').order_by('?')[:10]

        context = {
            'trending_places': trending_places,
            'nearby_places': nearby_places,
            'recommendations': recommendations,
        }
        return render(request, 'places/home.html', context)

class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        location = request.GET.get('location', '')
        min_rating = request.GET.get('min_rating', '0')
        price = request.GET.get('price', '')

        results = Place.objects.filter(is_approved=True)

        if query:
            results = results.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(tags__icontains=query)
            )
        if location:
            results = results.filter(address__icontains=location)
        if min_rating and min_rating != '0':
            results = results.filter(average_rating__gte=float(min_rating))
        if price:
            results = results.filter(price_level=price)

        return render(request, 'places/search.html', {'results': results})

class AddPlaceView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddPlaceForm()
        return render(request, 'places/add_place.html', {'form': form})

    def post(self, request):
        if request.method == 'POST':
            form = AddPlaceForm(request.POST, request.FILES)
            if form.is_valid():
                place = form.save(commit=False)
                
                if 'photo' in request.FILES:
                    place.photo = request.FILES['photo']
                
                place.save()
                return redirect('place_detail', pk=place.pk)
        else:
            form = AddPlaceForm()
        return render(request, 'places/add_place.html', {'form': form})


class AddReviewView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddReviewForm()
        return render(request, 'places/add_review.html', {'form': form})

    def post(self, request):
        form = AddReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('place_detail', pk=review.place.pk)
        return render(request, 'places/add_review.html', {'form': form})


class PlaceDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        place = get_object_or_404(Place, pk=pk)
        review_form = ReviewFormForDetailPage()
        return render(request, 'places/place_detail.html', {'place': place, 'review_form': review_form})

    def post(self, request, pk):
        place = get_object_or_404(Place, pk=pk)
        review_form = ReviewFormForDetailPage(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.place = place 
            review.save()
            messages.success(request, 'Thank you! Your review has been added.')
            return redirect('place_detail', pk=pk)
        
        return render(request, 'places/place_detail.html', {'place': place, 'review_form': review_form})