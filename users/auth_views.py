from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from .models import UserProfile, FoodProvider
from django.contrib import messages

User = get_user_model()

@login_required
def role_selection(request):
    profile = request.user.profile
    
    if profile.role != 'pending':
        return redirect('dashboard')
        
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in dict(UserProfile._meta.get_field('role').choices):
            profile.role = role
            
            # Additional logic for students (selecting a provider)
            if role == 'student':
                provider_id = request.POST.get('food_provider')
                if provider_id:
                    profile.food_provider_id = provider_id
            
            # Additional logic for NGO
            if role == 'ngo':
                profile.organization = request.POST.get('organization', '')
                
            profile.save()
            messages.success(request, f"Welcome onboard! Your role as {role} has been set.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid role selected.")
            
    campus_providers = FoodProvider.objects.filter(provider_type__in=['canteen', 'hostel', 'mess'])
    return render(request, 'users/role_selection.html', {
        'campus_providers': campus_providers,
        'roles': [r for r in UserProfile._meta.get_field('role').choices if r[0] != 'pending' and r[0] != 'admin']
    })

def verify_otp(request):
    # OTP verification has been removed - users now go directly to dashboard
    return redirect('dashboard')

def resend_otp(request):
    # OTP verification has been removed - users now go directly to dashboard
    return redirect('dashboard')
