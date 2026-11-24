from django.contrib import admin

from .models import DatasetImport, ImportedRecord


@admin.register(DatasetImport)
class DatasetImportAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename',
        'source_department',
        'file_format',
        'processing_status',
        'total_records',
        'accepted_records',
        'rejected_records',
        'uploaded_at',
    )
    list_filter = ('source_department', 'file_format', 'processing_status')
    search_fields = ('original_filename',)


@admin.register(ImportedRecord)
class ImportedRecordAdmin(admin.ModelAdmin):
    list_display = (
        'dataset_import',
        'row_number',
        'source_department',
        'accepted',
    )
    list_filter = ('source_department', 'accepted')
