from django.urls import path
from . import views

urlpatterns = [
    path('', views.surplus_list, name='surplus_list'),
    path('add/', views.add_surplus, name='add_surplus'),
    path('request/<int:surplus_id>/', views.request_surplus, name='request_surplus'),
    path('collected/<int:surplus_id>/', views.mark_collected, name='mark_collected'),
    path('delete/<int:surplus_id>/', views.delete_surplus, name='delete_surplus'),
]
