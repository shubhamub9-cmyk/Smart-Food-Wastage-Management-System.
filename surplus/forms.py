from django import forms
from django.utils import timezone
from .models import SurplusFood

class SurplusFoodForm(forms.ModelForm):
    class Meta:
        model = SurplusFood
        fields = ['food_name', 'quantity', 'unit', 'expiry_date', 'notes']
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cooked Rice, Bread'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'kg, servings, pieces'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any additional details'}),
        }
