from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = [
    ('pending', 'Pending Selection'),
    ('student', 'Student'),
    ('admin', 'Admin'),
    ('canteen', 'Canteen'),
    ('hostel', 'Hostel'),
    ('mess', 'Mess'),
    ('hotel', 'Hotel'),
    ('restaurant', 'Restaurant'),
    ('temple', 'Temple'),
    ('ngo', 'NGO'),
]

PROVIDER_TYPE_CHOICES = [
    ('canteen', 'Canteen'),
    ('hostel', 'Hostel'),
    ('mess', 'Mess'),
    ('hotel', 'Hotel'),
    ('restaurant', 'Restaurant'),
    ('temple', 'Temple'),
]

class FoodProvider(models.Model):
    name = models.CharField(max_length=200)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_TYPE_CHOICES)
    location = models.CharField(max_length=200, blank=True)
    managed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_provider'
    )

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"

    def is_campus_provider(self):
        return self.provider_type in ['canteen', 'hostel', 'mess']

    def is_global_provider(self):
        return self.provider_type in ['hotel', 'restaurant', 'temple']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pending')
    phone = models.CharField(max_length=15, blank=True)
    organization = models.CharField(max_length=100, blank=True, help_text="For NGO users")
    food_provider = models.ForeignKey(
        FoodProvider, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='members', help_text="Food Provider this user belongs to"
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_student(self):
        return self.role == 'student'

    def is_admin(self):
        return self.role == 'admin'

    def is_ngo(self):
        return self.role == 'ngo'

    def is_provider(self):
        return self.role in ['canteen', 'hostel', 'mess', 'hotel', 'restaurant', 'temple']

    def is_campus_provider(self):
        return self.role in ['canteen', 'hostel', 'mess']

    def is_global_provider(self):
        return self.role in ['hotel', 'restaurant', 'temple']

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class EmailOTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        from django.utils import timezone
        from datetime import timedelta
        return (timezone.now() - self.created_at) < timedelta(minutes=5) and not self.is_verified

    def __str__(self):
        return f"OTP for {self.email} ({self.otp_code})"

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance)
