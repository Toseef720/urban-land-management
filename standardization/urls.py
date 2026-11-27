
from django.urls import path

from . import views


urlpatterns = [
    path('', views.standardization_home, name='standardization_home'),
    path('<int:result_id>/', views.standardization_detail, name='standardization_detail'),
]
