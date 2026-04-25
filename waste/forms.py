from django import forms
from django.utils import timezone
from .models import WasteLog

class WasteLogForm(forms.ModelForm):
    class Meta:
        model = WasteLog
        fields = ['food_name', 'quantity', 'unit', 'category', 'date', 'image', 'notes']
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Rice, Dal, Vegetables'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
