from django.db import models


class DatasetImport(models.Model):
    DEPARTMENT_LAND = 'land'
    DEPARTMENT_TAX = 'tax'
    DEPARTMENT_UTILITY = 'utility'

    DEPARTMENT_CHOICES = [
        (DEPARTMENT_LAND, 'Land Department'),
        (DEPARTMENT_TAX, 'Property Tax Department'),
        (DEPARTMENT_UTILITY, 'Utility Department'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_COMPLETED_WITH_ERRORS = 'completed_with_errors'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_COMPLETED_WITH_ERRORS, 'Completed with errors'),
        (STATUS_FAILED, 'Failed'),
    ]

    source_department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES,
    )
    original_filename = models.CharField(max_length=255)
    file_format = models.CharField(max_length=10)
    source_file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    total_records = models.PositiveIntegerField(default=0)
    accepted_records = models.PositiveIntegerField(default=0)
    rejected_records = models.PositiveIntegerField(default=0)
    error_summary = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.original_filename} ({self.get_source_department_display()})'


class ImportedRecord(models.Model):
    dataset_import = models.ForeignKey(
        DatasetImport,
        on_delete=models.CASCADE,
        related_name='records',
    )
    row_number = models.PositiveIntegerField()
    source_department = models.CharField(max_length=20)
    accepted = models.BooleanField(default=False)
    original_data = models.JSONField(default=dict)
    normalized_data = models.JSONField(default=dict)
    validation_errors = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['row_number']

    def __str__(self):
        return f'Record {self.row_number} - {self.dataset_import.original_filename}'
