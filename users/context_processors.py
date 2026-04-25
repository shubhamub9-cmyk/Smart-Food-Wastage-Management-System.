from django.utils import timezone
from datetime import timedelta
from .models import Notification

def get_target_date(now):
    """Calculates target date exactly as the booking view does."""
    current_hour = now.hour
    is_open = (current_hour >= 20 or current_hour < 7)
    
    if current_hour >= 20:
        return now.date() + timedelta(days=1), is_open
    else:
        return now.date(), is_open

def notifications_processor(request):
    if not request.user.is_authenticated:
        return {}

    notifications = list(Notification.objects.filter(user=request.user).order_by('-created_at')[:10])
    
    # Inject real-time alerts without touching the DB for every single page load
    if hasattr(request.user, 'profile') and request.user.profile.is_student():
        now = timezone.localtime()
        target_date, is_open = get_target_date(now)
        current_hour = now.hour
        
        # Debug prints
        print(f"DEBUG CP: Current Local Time: {now}")
        print(f"DEBUG CP: Current Hour: {current_hour}")
        print(f"DEBUG CP: Booking Is Open: {is_open}")
        
        system_alerts = []
        
        if is_open:
            if current_hour >= 20:
                system_alerts.append({
                    'message': "Meal booking is now OPEN. Please book your meals.",
                    'is_system': True,
                    'is_read': False,
                    'created_at': now
                })
            elif current_hour < 7:
                system_alerts.append({
                    'message': "Meal booking will close soon at 7:00 AM",
                    'is_system': True,
                    'is_read': False,
                    'created_at': now
                })
        else:
            system_alerts.append({
                'message': "Meal booking is closed. Opens at 8:00 PM",
                'is_system': True,
                'is_read': False,
                'created_at': now
            })
                
        # Merge physical and ephemeral notifications
        all_notifications = system_alerts + notifications
        unread_count = sum(1 for n in all_notifications if not getattr(n, 'is_read', False) and not isinstance(n, dict))
        unread_count += len(system_alerts)
        
        return {
            'notifications': all_notifications,
            'unread_notifications_count': unread_count,
            'booking_is_open': is_open,
            'booking_target_date': target_date
        }
        
    return {
        'notifications': notifications,
        'unread_notifications_count': sum(1 for n in notifications if not n.is_read)
    }
