from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, FoodProvider, ROLE_CHOICES


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    phone = forms.CharField(max_length=15, required=False)
    organization = forms.CharField(max_length=100, required=False, help_text="Required for NGO users")

    # For Students: Dropdown of Campus Providers
    provider_selection = forms.ModelChoiceField(
        queryset=FoodProvider.objects.filter(provider_type__in=['canteen', 'hostel', 'mess']),
        required=False,
        empty_label="-- Select your provider --",
        help_text="Required for Students"
    )

    # For Providers: Name & Location of their establishment
    provider_name = forms.CharField(max_length=200, required=False, help_text="Name of your Canteen/Hotel/etc.")
    provider_location = forms.CharField(max_length=200, required=False, help_text="Location")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            role = self.cleaned_data['role']
            food_provider = None

            if role == 'student':
                food_provider = self.cleaned_data.get('provider_selection')
            elif role in ['canteen', 'hostel', 'mess', 'hotel', 'restaurant', 'temple']:
                # Auto-create the provider
                provider_name = self.cleaned_data.get('provider_name')
                provider_location = self.cleaned_data.get('provider_location')
                if provider_name:
                    food_provider = FoodProvider.objects.create(
                        name=provider_name,
                        provider_type=role,
                        location=provider_location,
                        managed_by=user
                    )

            # Update the profile created by signals
            profile = user.profile
            profile.role = role
            profile.phone = self.cleaned_data.get('phone', '')
            profile.organization = self.cleaned_data.get('organization', '')
            profile.food_provider = food_provider
            profile.save()

        return user
