from django.urls import path
from . import views

urlpatterns = [
    path('', views.waste_list, name='waste_list'),
    path('log/', views.log_waste, name='log_waste'),
    path('delete/<int:log_id>/', views.delete_waste_log, name='delete_waste_log'),
]
