from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import FoodProvider

CATEGORY_CHOICES = [
    ('edible', 'Edible'),
    ('inedible', 'Inedible'),
]

class WasteLog(models.Model):
    food_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='waste_images/', blank=True, null=True)
    notes = models.TextField(blank=True)
    logged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='waste_logs'
    )
    food_provider = models.ForeignKey(
        FoodProvider, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='waste_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.food_name} - {self.quantity}{self.unit} ({self.category}) on {self.date}"
