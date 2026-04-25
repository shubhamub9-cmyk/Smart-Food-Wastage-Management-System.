from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import FoodProvider

STATUS_CHOICES = [
    ('available', 'Available'),
    ('requested', 'Requested'),
    ('collected', 'Collected'),
]

class SurplusFood(models.Model):
    food_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='surplus_added')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='surplus_requested')
    food_provider = models.ForeignKey(
        FoodProvider, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='surplus_items'
    )
    date_added = models.DateField(default=timezone.now)
    date_requested = models.DateTimeField(null=True, blank=True)
    date_collected = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.food_name} - {self.quantity} {self.unit} ({self.status})"
