from django.urls import path
from . import views, auth_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('role-selection/', auth_views.role_selection, name='role_selection'),
    path('verify-otp/', auth_views.verify_otp, name='verify_otp'),
    path('resend-otp/', auth_views.resend_otp, name='resend_otp'),
]
