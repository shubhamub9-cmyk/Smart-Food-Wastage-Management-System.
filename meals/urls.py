from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_meal, name='book_meal'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('menu/', views.meal_menu, name='meal_menu'),
    path('menu/update/', views.update_menu, name='update_menu'),
]
