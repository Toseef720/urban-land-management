from django.urls import path
from . import views

urlpatterns = [
    path('', views.harmonization_home, name='harmonization_home'),
    path(
        'unmatched/',
        views.unmatched_records,
        name='unmatched_records'
    ),
    path(
        'unmatched/<int:record_id>/',
        views.unmatched_record_detail,
        name='unmatched_record_detail'
    ),
    path(
        'unmatched/<int:record_id>/match/',
        views.manual_match,
        name='manual_match'
    ),
]