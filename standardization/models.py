
from django.db import models
from datasets.models import ImportedRecord


class StandardizationResult(models.Model):
    source_record = models.OneToOneField(
        ImportedRecord,
        on_delete=models.CASCADE,
        related_name='standardization_result'
    )
    standardized_data = models.JSONField(default=dict)
    is_valid = models.BooleanField(default=True)
    errors = models.TextField(blank=True)
    processed_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-processed_at']
    def __str__(self):
        return f'Standardized Record {self.source_record.id}'
