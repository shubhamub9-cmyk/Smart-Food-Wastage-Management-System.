from django.contrib import admin
from .models import WasteLog

@admin.register(WasteLog)
class WasteLogAdmin(admin.ModelAdmin):
    list_display = ['food_name', 'quantity', 'unit', 'category', 'date', 'logged_by']
    list_filter = ['category', 'date']
    search_fields = ['food_name', 'logged_by']
    date_hierarchy = 'date'
