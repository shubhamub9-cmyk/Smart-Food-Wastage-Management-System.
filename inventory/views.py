from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import FoodItem
from .forms import FoodItemForm


def _get_provider(request):
    """Get provider for current user, or None."""
    try:
        return request.user.profile.food_provider
    except Exception:
        return None


@login_required
def inventory_list(request):
    today = timezone.now().date()
    provider = _get_provider(request)

    # Providers see only their inventory; admins see all
    try:
        is_admin = request.user.profile.is_admin() or request.user.is_superuser
    except Exception:
        is_admin = request.user.is_superuser

    if is_admin:
        items = FoodItem.objects.all().order_by('expiry_date')
    elif provider:
        items = FoodItem.objects.filter(food_provider=provider).order_by('expiry_date')
    else:
        items = FoodItem.objects.none()

    expired = items.filter(expiry_date__lt=today)
    expiring_soon = items.filter(expiry_date__range=[today, today + timedelta(days=2)])
    good_items = items.filter(expiry_date__gt=today + timedelta(days=2))

    context = {
        'items': items,
        'expired': expired,
        'expiring_soon': expiring_soon,
        'good_items': good_items,
        'today': today,
    }
    return render(request, 'inventory/list.html', context)


@login_required
def add_item(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            # Auto-assign provider
            item.food_provider = _get_provider(request)
            item.save()
            messages.success(request, 'Food item added to inventory.')
            return redirect('inventory_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FoodItemForm()
    return render(request, 'inventory/add_item.html', {'form': form})


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully.')
            return redirect('inventory_list')
    else:
        form = FoodItemForm(instance=item)
    return render(request, 'inventory/edit_item.html', {'form': form, 'item': item})


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted from inventory.')
        return redirect('inventory_list')
    return render(request, 'inventory/confirm_delete.html', {'item': item})
