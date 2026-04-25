from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import FoodProvider

MEAL_TYPE_CHOICES = [
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
]

STATUS_CHOICES = [
    ('booked', 'Booked'),
    ('cancelled', 'Cancelled'),
    ('consumed', 'Consumed'),
]

class MealBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    food_provider = models.ForeignKey(
        FoodProvider, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='meal_bookings'
    )
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date', 'meal_type']
        ordering = ['-date', 'meal_type']

    def __str__(self):
        return f"{self.user.username} - {self.meal_type} on {self.date}"


class MenuItem(models.Model):
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.meal_type}: {self.name}"

class WeeklyMenu(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
    ]
    provider = models.ForeignKey(FoodProvider, on_delete=models.CASCADE, related_name='weekly_menus')
    day = models.CharField(max_length=15, choices=DAY_CHOICES)
    breakfast = models.TextField(blank=True)
    lunch = models.TextField(blank=True)
    dinner = models.TextField(blank=True)

    class Meta:
        unique_together = ['provider', 'day']

    def __str__(self):
        return f"{self.provider.name} - {self.day} Menu"
