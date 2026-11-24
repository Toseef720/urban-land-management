from django.urls import path

from . import views


urlpatterns = [
    path('', views.dataset_home, name='dataset_home'),
    path('<int:import_id>/', views.dataset_detail, name='dataset_detail'),
]
