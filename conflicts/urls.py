from django.urls import path

from . import views


urlpatterns = [
    path('', views.conflict_dashboard, name='conflict_dashboard'),
    path('<int:conflict_id>/', views.conflict_detail, name='conflict_detail'),
    path(
        '<int:conflict_id>/resolve/',
        views.resolve_conflict,
        name='resolve_conflict',
    ),
]
