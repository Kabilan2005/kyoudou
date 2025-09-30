from django.contrib import admin
from .models import Place

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'sub_type', 'price_level', 'is_approved', 'average_rating', 'added_by')
    list_filter = ('type', 'sub_type', 'price_level', 'is_approved', 'reported')
    search_fields = ('name', 'address', 'description')
    actions = ['approve_places', 'mark_reported']

    def approve_places(self, request, queryset):
        queryset.update(is_approved=True)
    approve_places.short_description = "Approve selected places"

    def mark_reported(self, request, queryset):
        queryset.update(reported=True)
    mark_reported.short_description = "Mark selected as reported"

admin.site.register(Place, PlaceAdmin)