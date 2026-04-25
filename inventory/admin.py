from django.contrib import admin
from .models import FoodItem

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'expiry_date', 'added_on']
    list_filter = ['expiry_date']
    search_fields = ['name']
    ordering = ['expiry_date']
