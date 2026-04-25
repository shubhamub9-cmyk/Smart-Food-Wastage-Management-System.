from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SurplusFood
from .forms import SurplusFoodForm


def _get_provider(request):
    try:
        return request.user.profile.food_provider
    except Exception:
        return None


@login_required
def surplus_list(request):
    # Depending on role, show different surplus
    try:
        profile = request.user.profile
        is_ngo = profile.is_ngo()
        is_admin = profile.is_admin() or request.user.is_superuser
        provider = _get_provider(request)
    except Exception:
        is_ngo = False
        is_admin = False
        provider = None

    if is_ngo or is_admin:
        # NGOs see all available food
        available = SurplusFood.objects.filter(status='available')
        requested = SurplusFood.objects.filter(status='requested')
        collected = SurplusFood.objects.filter(status='collected')
    elif provider:
        # Providers only see their own surplus
        available = SurplusFood.objects.filter(food_provider=provider, status='available')
        requested = SurplusFood.objects.filter(food_provider=provider, status='requested')
        collected = SurplusFood.objects.filter(food_provider=provider, status='collected')
    else:
        # Students shouldn't see surplus, or show none
        available = SurplusFood.objects.none()
        requested = SurplusFood.objects.none()
        collected = SurplusFood.objects.none()

    context = {
        'available': available,
        'requested': requested,
        'collected': collected,
        'is_ngo': is_ngo,
    }
    return render(request, 'surplus/list.html', context)


@login_required
def add_surplus(request):
    if request.method == 'POST':
        form = SurplusFoodForm(request.POST)
        if form.is_valid():
            surplus = form.save(commit=False)
            surplus.added_by = request.user
            surplus.food_provider = _get_provider(request)
            surplus.save()
            messages.success(request, 'Surplus food entry added successfully.')
            return redirect('surplus_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SurplusFoodForm()
    return render(request, 'surplus/add_surplus.html', {'form': form})


@login_required
def request_surplus(request, surplus_id):
    profile = request.user.profile
    if not profile.is_ngo():
        messages.error(request, 'Only NGOs can request surplus food.')
        return redirect('surplus_list')

    surplus = get_object_or_404(SurplusFood, id=surplus_id)
    
    if surplus.status != 'available':
        messages.error(request, f'This food has already been {surplus.status}.')
        return redirect('surplus_list')
        
    surplus.status = 'requested'
    surplus.requested_by = request.user
    surplus.date_requested = timezone.now()
    surplus.save()
    messages.success(request, 'Food request sent successfully. Please contact the provider for pickup.')
    return redirect('surplus_list')


@login_required
def mark_collected(request, surplus_id):
    surplus = get_object_or_404(SurplusFood, id=surplus_id)
    profile = request.user.profile
    
    # Only the requesting NGO or the original Provider can mark as collected
    is_requester = (surplus.requested_by == request.user)
    is_provider = (surplus.food_provider == profile.food_provider if hasattr(profile, 'food_provider') else False)
    
    if not (is_requester or is_provider or request.user.is_superuser):
        messages.error(request, 'You do not have permission to update this entry.')
        return redirect('surplus_list')

    if surplus.status == 'collected':
        messages.error(request, 'This food has already been marked as collected.')
        return redirect('surplus_list')
        
    surplus.status = 'collected'
    surplus.date_collected = timezone.now()
    surplus.save()
    messages.success(request, 'Marked as collected successfully. Thank you for preventing waste!')
    return redirect('surplus_list')


@login_required
def delete_surplus(request, surplus_id):
    surplus = get_object_or_404(SurplusFood, id=surplus_id)
    profile = request.user.profile
    
    # Only the Provider who added it can delete it
    is_provider = (surplus.food_provider == profile.food_provider if hasattr(profile, 'food_provider') else False)
    
    if not (is_provider or request.user.is_superuser):
        messages.error(request, 'Only the food provider can delete this surplus entry.')
        return redirect('surplus_list')

    if request.method == 'POST':
        surplus.delete()
        messages.success(request, 'Surplus entry deleted.')
        return redirect('surplus_list')
    return render(request, 'surplus/confirm_delete.html', {'surplus': surplus})
