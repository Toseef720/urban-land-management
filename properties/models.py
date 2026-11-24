
from django.db import models


class Property(models.Model):
    parcel_id = models.CharField(max_length=50, unique=True)
    property_name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=150)
    address = models.TextField()
    area = models.FloatField()
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='property_photos/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.parcel_id
