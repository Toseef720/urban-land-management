from django.db import models

# Create your models here.
from django.db import models

from properties.models import Property
from standardization.models import StandardizationResult


class Conflict(models.Model):
    FIELD_PERSON_NAME = 'person_name'
    FIELD_ADDRESS = 'address'
    FIELD_LAND_AREA_SQM = 'land_area_sqm'

    FIELD_CHOICES = [
        (FIELD_PERSON_NAME, 'Person name'),
        (FIELD_ADDRESS, 'Address'),
        (FIELD_LAND_AREA_SQM, 'Land area (sq m)'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLEARED = 'cleared'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLEARED, 'Cleared'),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='conflicts',
    )
    field_name = models.CharField(max_length=30, choices=FIELD_CHOICES)
    snapshot_key = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f'{self.property.parcel_id} - {self.get_field_name_display()}'


class ConflictValue(models.Model):
    conflict = models.ForeignKey(
        Conflict,
        on_delete=models.CASCADE,
        related_name='values',
    )
    standardization_result = models.ForeignKey(
        StandardizationResult,
        on_delete=models.PROTECT,
        related_name='conflict_values',
    )
    value_snapshot = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['conflict', 'standardization_result'],
                name='unique_conflict_source_result',
            ),
        ]

    def __str__(self):
        return f'{self.conflict} - {self.standardization_result}'


class ConflictResolution(models.Model):
    conflict = models.OneToOneField(
        Conflict,
        on_delete=models.CASCADE,
        related_name='resolution',
    )
    resolved_value = models.TextField()
    resolution_note = models.TextField()
    resolved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Resolution for {self.conflict}'
