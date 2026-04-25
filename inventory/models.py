from django.db import models
from django.utils import timezone
from datetime import timedelta
from users.models import FoodProvider


class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')
    expiry_date = models.DateField()
    added_on = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    food_provider = models.ForeignKey(
        FoodProvider, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='inventory_items'
    )

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def expires_soon(self):
        return self.expiry_date <= timezone.now().date() + timedelta(days=2)

    def expires_today(self):
        return self.expiry_date == timezone.now().date()

    def expires_tomorrow(self):
        return self.expiry_date == timezone.now().date() + timedelta(days=1)
