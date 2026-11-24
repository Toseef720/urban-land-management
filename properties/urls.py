from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('add/', views.add_property, name='add_property'),
    path('edit/<int:property_id>/', views.edit_property, name='edit_property'),
    path('delete/<int:property_id>/', views.delete_property, name='delete_property'),
]