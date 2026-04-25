from django.contrib import admin
from .models import MealBooking, MenuItem

@admin.register(MealBooking)
class MealBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'meal_type', 'status', 'created_at']
    list_filter = ['meal_type', 'status', 'date']
    search_fields = ['user__username']
    date_hierarchy = 'date'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'day_of_week']
    list_filter = ['meal_type', 'day_of_week']
