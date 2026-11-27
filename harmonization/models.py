from django.db import models
from properties.models import Property
from standardization.models import StandardizationResult


class HarmonizedRecord(models.Model):

    STATUS_MATCHED = 'matched'
    STATUS_UNMATCHED = 'unmatched'
    STATUS_INVALID = 'invalid'

    STATUS_CHOICES = [
        (STATUS_MATCHED, 'Matched'),
        (STATUS_UNMATCHED, 'Unmatched'),
        (STATUS_INVALID, 'Invalid'),
    ]

    standardization_result = models.OneToOneField(
        StandardizationResult,
        on_delete=models.CASCADE,
        related_name='harmonization'
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='harmonized_records'
    )

    match_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_UNMATCHED
    )

    match_method = models.CharField(
        max_length=50,
        blank=True
    )

    processed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-processed_at']

    def __str__(self):
        return f'Harmonization Record {self.id}'