from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from meals.models import MealBooking
from inventory.models import FoodItem
from waste.models import WasteLog
from surplus.models import SurplusFood
from users.models import UserProfile, FoodProvider


def _get_user_provider(user):
    """Helper: get the food provider linked to this user's profile."""
    try:
        return user.profile.food_provider
    except Exception:
        return None


@login_required
def dashboard_view(request):
    """Route users to appropriate dashboard based on role."""
    try:
        profile = request.user.profile
    except Exception:
        return redirect('student_dashboard')

    if profile.is_admin():
        return redirect('admin_stats')
    elif profile.is_ngo():
        return redirect('ngo_dashboard')
    elif profile.is_provider():
        return redirect('provider_dashboard')
    else:
        return redirect('student_dashboard')


@login_required
def student_dashboard(request):
    if hasattr(request.user, 'profile') and not request.user.profile.is_student() and not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')

    today = timezone.now().date()
    # Only show THIS student's bookings
    bookings = MealBooking.objects.filter(user=request.user).order_by('-date')[:10]
    today_bookings = MealBooking.objects.filter(user=request.user, date=today)
    provider = _get_user_provider(request.user)

    # Calculate if booking is open (8 PM to 7 AM)
    now_local = timezone.localtime()
    current_hour = now_local.hour
    booking_is_open = (current_hour >= 20 or current_hour < 7)

    context = {
        'bookings': bookings,
        'today_bookings': today_bookings,
        'today': today,
        'role': 'student',
        'provider': provider,
        'booking_is_open': booking_is_open,
    }
    return render(request, 'dashboard/student.html', context)


@login_required
def provider_dashboard(request):
    if hasattr(request.user, 'profile') and not request.user.profile.is_provider() and not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')

    today = timezone.now().date()
    provider = _get_user_provider(request.user)
    is_campus = request.user.profile.is_campus_provider()

    # ---- FILTER EVERYTHING BY THIS PROVIDER ----
    bookings_qs = MealBooking.objects.filter(food_provider=provider) if provider and is_campus else MealBooking.objects.none()

    today_total = bookings_qs.filter(date=today, status='booked').count()
    today_breakfast = bookings_qs.filter(date=today, meal_type='breakfast', status='booked').count()
    today_lunch = bookings_qs.filter(date=today, meal_type='lunch', status='booked').count()
    today_dinner = bookings_qs.filter(date=today, meal_type='dinner', status='booked').count()

    # Tomorrow's sightings (useful after 8 PM)
    tomorrow = today + timedelta(days=1)
    tomorrow_total = bookings_qs.filter(date=tomorrow, status='booked').count()

    # Total students registered in this provider (if campus provider)
    total_students = UserProfile.objects.filter(food_provider=provider, role='student').count() if (provider and is_campus) else 0

    # Demand prediction: average of last 3 days bookings for THIS provider
    last_3_days = []
    if is_campus:
        for i in range(1, 4):
            day = today - timedelta(days=i)
            count = bookings_qs.filter(date=day, status='booked').count()
            last_3_days.append(count)

    avg_demand = sum(last_3_days) / 3 if last_3_days else 0
    predicted_demand = round(avg_demand)

    # Expiring inventory for THIS provider
    inventory_qs = FoodItem.objects.filter(food_provider=provider) if provider else FoodItem.objects.none()
    expiring_items = inventory_qs.filter(
        expiry_date__lte=today + timedelta(days=2),
        expiry_date__gte=today
    )

    # Waste for THIS provider
    waste_qs = WasteLog.objects.filter(food_provider=provider) if provider else WasteLog.objects.none()
    total_waste = waste_qs.aggregate(total=Sum('quantity'))['total'] or 0

    # Surplus for THIS provider
    surplus_qs = SurplusFood.objects.filter(food_provider=provider) if provider else SurplusFood.objects.none()
    total_surplus = surplus_qs.count()

    # Last 7 days bookings for trend
    daily_bookings = []
    if is_campus:
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = bookings_qs.filter(date=day, status='booked').count()
            daily_bookings.append({'date': day.strftime('%d %b'), 'count': count})

    context = {
        'today': today,
        'today_total': today_total,
        'today_breakfast': today_breakfast,
        'today_lunch': today_lunch,
        'today_dinner': today_dinner,
        'tomorrow_total': tomorrow_total,
        'total_students': total_students,
        'predicted_demand': predicted_demand,
        'last_3_days': last_3_days,
        'expiring_items': expiring_items,
        'daily_bookings': daily_bookings,
        'total_waste': total_waste,
        'total_surplus': total_surplus,
        'provider': provider,
        'is_campus': is_campus,
        'role': request.user.profile.role,
    }
    return render(request, 'dashboard/provider.html', context)


@login_required
def admin_stats(request):
    """Admin dashboard with GLOBAL statistics (all providers)."""
    if hasattr(request.user, 'profile') and not request.user.profile.is_admin() and not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')

    today = timezone.now().date()

    total_bookings = MealBooking.objects.filter(status='booked').count()
    today_bookings = MealBooking.objects.filter(date=today, status='booked').count()

    total_providers = FoodProvider.objects.count()

    total_waste = WasteLog.objects.aggregate(total=Sum('quantity'))['total'] or 0
    edible_waste = WasteLog.objects.filter(category='edible').aggregate(total=Sum('quantity'))['total'] or 0
    inedible_waste = WasteLog.objects.filter(category='inedible').aggregate(total=Sum('quantity'))['total'] or 0

    avg_meal_cost = 50
    waste_reduction_pct = 30
    reduced_waste = float(total_waste) * 0.3
    cost_saved = reduced_waste * avg_meal_cost

    total_surplus = SurplusFood.objects.count()
    collected_surplus = SurplusFood.objects.filter(status='collected').count()

    expiring_items = FoodItem.objects.filter(
        expiry_date__lte=today + timedelta(days=2),
        expiry_date__gte=today
    ).count()
    expired_items = FoodItem.objects.filter(expiry_date__lt=today).count()

    last_3_days_total = 0
    for i in range(1, 4):
        day = today - timedelta(days=i)
        last_3_days_total += MealBooking.objects.filter(date=day, status='booked').count()
    predicted_demand = round(last_3_days_total / 3)

    recent_waste = WasteLog.objects.order_by('-date')[:5]

    waste_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        qty = WasteLog.objects.filter(date=day).aggregate(total=Sum('quantity'))['total'] or 0
        waste_trend.append({'date': day.strftime('%d %b'), 'quantity': float(qty)})

    context = {
        'total_providers': total_providers,
        'total_bookings': total_bookings,
        'today_bookings': today_bookings,
        'total_waste': total_waste,
        'edible_waste': edible_waste,
        'inedible_waste': inedible_waste,
        'waste_reduction_pct': waste_reduction_pct,
        'cost_saved': cost_saved,
        'total_surplus': total_surplus,
        'collected_surplus': collected_surplus,
        'expiring_items': expiring_items,
        'expired_items': expired_items,
        'predicted_demand': predicted_demand,
        'recent_waste': recent_waste,
        'waste_trend': waste_trend,
        'role': 'admin',
    }
    return render(request, 'dashboard/admin.html', context)


@login_required
def ngo_dashboard(request):
    if hasattr(request.user, 'profile') and not request.user.profile.is_ngo() and not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')

    # NGO sees ALL available surplus
    available_surplus = SurplusFood.objects.filter(status='available')
    my_requests = SurplusFood.objects.filter(requested_by=request.user)
    context = {
        'available_surplus': available_surplus,
        'my_requests': my_requests,
        'role': 'ngo',
    }
    return render(request, 'dashboard/ngo.html', context)


@login_required
def registered_students(request):
    """List of students registered with a provider."""
    if hasattr(request.user, 'profile') and not request.user.profile.is_provider() and not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')

    provider = _get_user_provider(request.user)
    if not provider:
        messages.error(request, 'No provider associated with your account.')
        return redirect('dashboard')

    students = UserProfile.objects.filter(food_provider=provider, role='student').select_related('user')
    
    context = {
        'provider': provider,
        'students': students,
        'role': 'provider'
    }
    return render(request, 'users/student_list.html', context)

