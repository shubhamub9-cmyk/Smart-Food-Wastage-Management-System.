from django.contrib import admin
from .models import SurplusFood

@admin.register(SurplusFood)
class SurplusFoodAdmin(admin.ModelAdmin):
    list_display = ['food_name', 'quantity', 'unit', 'status', 'date_added', 'added_by', 'requested_by']
    list_filter = ['status']
    search_fields = ['food_name']
