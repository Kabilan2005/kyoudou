from django import forms
from .models import Place

class AddPlaceForm(forms.ModelForm):
    photo = forms.ImageField(required=False) 
    # As of now Only one photo is allowed
    # This will be definitely scaled to accept multiple photos

    class Meta:
        model = Place
        fields = [
            'name', 'type', 'sub_type', 'address', 'latitude', 'longitude', 
            'price_level', 'description', 'contact_info', 'tags',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'sub_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_level': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., cozy, late-night, wifi'}),
        }
