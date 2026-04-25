from django import forms
from django.utils import timezone
from .models import MealBooking

class MealBookingForm(forms.ModelForm):
    class Meta:
        model = MealBooking
        fields = ['date', 'meal_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': str(timezone.now().date())}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }
