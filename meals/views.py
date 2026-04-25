from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import MealBooking, WeeklyMenu
from .forms import MealBookingForm
from users.models import Notification


from datetime import timedelta

@login_required
def book_meal(request):
    # Only students can book meals
    if not request.user.profile.is_student() and not request.user.is_superuser:
        messages.error(request, 'Only students can book meals.')
        return redirect('dashboard')

    now = timezone.localtime()
    current_hour = now.hour
    
    # Debug prints
    print(f"DEBUG: Current Local Time: {now}")
    print(f"DEBUG: Current Hour: {current_hour}")
    
    # Correct Logic: 8 PM (20) to 7 AM
    booking_open = (current_hour >= 20 or current_hour < 7)
    
    print(f"DEBUG: Booking Open Status: {booking_open}")

    # Set target date (if booking after 8 PM, it's for tomorrow; if before 7 AM, it's for today)
    if current_hour >= 20:
        target_date = now.date() + timedelta(days=1)
    else:
        target_date = now.date()

    if request.method == 'POST' and booking_open:
        meal_types = request.POST.getlist('meal_types')
        if not meal_types:
            messages.error(request, 'Please select at least one meal to book.')
        else:
            success_count = 0
            for mt in meal_types:
                if not MealBooking.objects.filter(user=request.user, date=target_date, meal_type=mt).exists():
                    booking = MealBooking(
                        user=request.user,
                        date=target_date,
                        meal_type=mt
                    )
                    # Explicitly link booking to student's provider
                    if hasattr(request.user, 'profile'):
                        booking.food_provider = request.user.profile.food_provider
                    
                    booking.save()
                    success_count += 1
            
            if success_count > 0:
                Notification.objects.create(
                    user=request.user,
                    message=f"Successfully booked {success_count} meal(s) for {target_date.strftime('%b %d')}"
                )
                messages.success(request, f'Successfully booked {success_count} meal(s) for {target_date.strftime("%b %d, %Y")}.')
                return redirect('my_bookings')
            else:
                messages.error(request, 'You have already booked these meals for this date.')

    # Get menus for the target date from WeeklyMenu
    day_name = target_date.strftime('%A')
    try:
        provider = request.user.profile.food_provider
        todays_menu = WeeklyMenu.objects.filter(provider=provider, day=day_name).first()
    except Exception:
        todays_menu = None

    context = {
        'target_date': target_date,
        'booking_open': booking_open,
        'todays_menu': todays_menu,
        'today': now.date()
    }
    return render(request, 'meals/book_meal.html', context)


@login_required
def my_bookings(request):
    bookings = MealBooking.objects.filter(user=request.user).order_by('-date')
    return render(request, 'meals/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(MealBooking, id=booking_id, user=request.user)
    if booking.date >= timezone.now().date():
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel past bookings.')
    return redirect('my_bookings')


@login_required
def meal_menu(request):
    try:
        provider = request.user.profile.food_provider
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        menus = []
        for day in day_names:
            menu = WeeklyMenu.objects.filter(provider=provider, day=day).first()
            if menu:
                menus.append(menu)
                
    except Exception:
        menus = []

    return render(request, 'meals/menu.html', {'menus': menus})

@login_required
def update_menu(request):
    try:
        provider = request.user.profile.food_provider
    except Exception:
        messages.error(request, 'Only campus providers can update the weekly menu.')
        return redirect('dashboard')
        
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    if request.method == 'POST':
        for day in days:
            breakfast = request.POST.get(f'breakfast_{day}', '')
            lunch = request.POST.get(f'lunch_{day}', '')
            dinner = request.POST.get(f'dinner_{day}', '')
            
            WeeklyMenu.objects.update_or_create(
                provider=provider,
                day=day,
                defaults={
                    'breakfast': breakfast,
                    'lunch': lunch,
                    'dinner': dinner
                }
            )
        messages.success(request, 'Weekly menu updated successfully.')
        return redirect('update_menu')
        
    menus = []
    for day in days:
        menu, _ = WeeklyMenu.objects.get_or_create(provider=provider, day=day)
        menus.append(menu)
        
    return render(request, 'meals/update_menu.html', {'menus': menus, 'days': days})
