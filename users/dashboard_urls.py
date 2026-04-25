from django.urls import path
from . import dashboard_views

urlpatterns = [
    path('student/', dashboard_views.student_dashboard, name='student_dashboard'),
    path('provider/', dashboard_views.provider_dashboard, name='provider_dashboard'),
    path('canteen/', dashboard_views.provider_dashboard, name='canteen_dashboard'), # Fallback URL
    path('admin-stats/', dashboard_views.admin_stats, name='admin_stats'),
    path('ngo/', dashboard_views.ngo_dashboard, name='ngo_dashboard'),
    path('registered-students/', dashboard_views.registered_students, name='registered_students'),
    path('', dashboard_views.dashboard_view, name='dashboard'),
]
