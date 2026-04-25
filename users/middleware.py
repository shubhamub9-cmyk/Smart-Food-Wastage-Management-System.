from django.shortcuts import redirect
from django.urls import reverse

class RoleSelectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user has a profile and if role is 'pending'
            if hasattr(request.user, 'profile') and request.user.profile.role == 'pending':
                # Allowed paths that don't trigger redirect
                allowed_paths = [
                    reverse('role_selection'),
                    reverse('logout'),
                    '/admin/',
                    '/accounts/',
                ]
                
                # Check if current path starts with any allowed path
                path = request.path
                if not any(path.startswith(p) for p in allowed_paths):
                    return redirect('role_selection')

        response = self.get_response(request)
        return response
