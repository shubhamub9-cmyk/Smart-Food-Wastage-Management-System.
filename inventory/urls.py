from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('add/', views.add_item, name='add_inventory_item'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_inventory_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_inventory_item'),
]
