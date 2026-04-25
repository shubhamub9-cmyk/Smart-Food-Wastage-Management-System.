from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import WasteLog
from .forms import WasteLogForm


def _get_provider(request):
    try:
        return request.user.profile.food_provider
    except Exception:
        return None


@login_required
def waste_list(request):
    provider = _get_provider(request)

    try:
        is_admin = request.user.profile.is_admin() or request.user.is_superuser
    except Exception:
        is_admin = request.user.is_superuser

    if is_admin:
        logs = WasteLog.objects.all().order_by('-date')
    elif provider:
        logs = WasteLog.objects.filter(food_provider=provider).order_by('-date')
    else:
        logs = WasteLog.objects.none()

    total_waste = logs.aggregate(total=Sum('quantity'))['total'] or 0
    edible_waste = logs.filter(category='edible').aggregate(total=Sum('quantity'))['total'] or 0
    inedible_waste = logs.filter(category='inedible').aggregate(total=Sum('quantity'))['total'] or 0

    today = timezone.now().date()
    trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        if is_admin:
            qty = WasteLog.objects.filter(date=day).aggregate(total=Sum('quantity'))['total'] or 0
        elif provider:
            qty = WasteLog.objects.filter(date=day, food_provider=provider).aggregate(total=Sum('quantity'))['total'] or 0
        else:
            qty = 0
        trend.append({'date': day.strftime('%d %b'), 'quantity': float(qty)})

    context = {
        'logs': logs,
        'total_waste': total_waste,
        'edible_waste': edible_waste,
        'inedible_waste': inedible_waste,
        'trend': trend,
    }
    return render(request, 'waste/list.html', context)


@login_required
def log_waste(request):
    if request.method == 'POST':
        form = WasteLogForm(request.POST, request.FILES)
        if form.is_valid():
            log = form.save(commit=False)
            log.logged_by = request.user
            log.food_provider = _get_provider(request)
            log.save()
            
            # Critical Feature: Auto-convert edible waste directly to Surplus
            if log.category == 'edible':
                from surplus.models import SurplusFood
                surplus_notes = f"[Auto-generated from Edible Waste] {log.notes}".strip()
                SurplusFood.objects.create(
                    food_name=log.food_name,
                    quantity=log.quantity,
                    unit=log.unit,
                    status='available',
                    added_by=request.user,
                    food_provider=log.food_provider,
                    notes=surplus_notes
                )
                
            messages.success(request, 'Waste logged successfully. Edible items automatically dispatched to NGOs!' if log.category == 'edible' else 'Waste logged successfully.')
            return redirect('waste_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteLogForm()
    return render(request, 'waste/log_waste.html', {'form': form})


@login_required
def delete_waste_log(request, log_id):
    log = get_object_or_404(WasteLog, id=log_id)
    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Waste log deleted.')
        return redirect('waste_list')
    return render(request, 'waste/confirm_delete.html', {'log': log})
