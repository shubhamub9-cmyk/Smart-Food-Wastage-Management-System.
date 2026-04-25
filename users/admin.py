from django.contrib import admin
from .models import UserProfile, FoodProvider


@admin.register(FoodProvider)
class FoodProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider_type', 'location', 'managed_by']
    list_filter = ['provider_type']
    search_fields = ['name', 'location']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'food_provider', 'phone', 'organization']
    list_filter = ['role', 'food_provider']
    search_fields = ['user__username', 'user__email']
