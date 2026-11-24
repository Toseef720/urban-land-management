import csv
import json

from django.core.exceptions import ValidationError

from .models import DatasetImport, ImportedRecord


def process_dataset_import(dataset_import):
    dataset_import.processing_status = DatasetImport.STATUS_PROCESSING
    dataset_import.error_summary = ''
    dataset_import.save(update_fields=['processing_status', 'error_summary'])

    try:
        dataset_import.source_file.open('rb')
        if dataset_import.file_format == 'GEOJSON':
            return process_geojson(dataset_import)
        return process_csv(dataset_import)
    except (json.JSONDecodeError, UnicodeDecodeError, csv.Error, OSError, ValidationError) as exc:
        dataset_import.processing_status = DatasetImport.STATUS_FAILED
        dataset_import.error_summary = str(exc)
        dataset_import.save(update_fields=['processing_status', 'error_summary'])
        return
    finally:
        if dataset_import.source_file:
            dataset_import.source_file.close()


def process_csv(dataset_import):
    dataset_import.source_file.seek(0)
    text = dataset_import.source_file.read().decode('utf-8-sig')
    reader = csv.DictReader(text.splitlines())

    if dataset_import.source_department == DatasetImport.DEPARTMENT_TAX:
        required_columns = ['property_no', 'owner_name', 'address']
        required_values = ['property_no', 'owner_name', 'address']
    else:
        required_columns = ['property_id', 'consumer_name', 'meter_id', 'address', 'utility_type']
        required_values = required_columns

    missing_columns = [
        column for column in required_columns
        if column not in (reader.fieldnames or [])
    ]
    if missing_columns:
        dataset_import.processing_status = DatasetImport.STATUS_FAILED
        dataset_import.error_summary = (
            'Missing required CSV columns: ' + ', '.join(missing_columns)
        )
        dataset_import.save(update_fields=['processing_status', 'error_summary'])
        return

    process_csv_rows(dataset_import, reader, required_values)


def process_csv_rows(dataset_import, reader, required_values):
    total = accepted = rejected = 0
    error_messages = []

    for row_number, row in enumerate(reader, start=2):
        total += 1
        original = {key: (value.strip() if isinstance(value, str) else value)
                    for key, value in row.items()}
        errors = []

        for column in required_values:
            if not original.get(column):
                errors.append(f'Missing required value: {column}')

        if dataset_import.source_department == DatasetImport.DEPARTMENT_TAX:
            normalized = {
                'property_no': original.get('property_no', ''),
                'owner_name': original.get('owner_name', ''),
                'address': original.get('address', ''),
                'tax_amount': original.get('tax_amount', ''),
                'tax_status': original.get('tax_status', ''),
            }
        else:
            normalized = {
                'property_id': original.get('property_id', ''),
                'consumer_name': original.get('consumer_name', ''),
                'meter_id': original.get('meter_id', ''),
                'address': original.get('address', ''),
                'utility_type': original.get('utility_type', ''),
            }

        if errors:
            rejected += 1
            error_messages.append(f'Row {row_number}: ' + '; '.join(errors))
        else:
            accepted += 1

        ImportedRecord.objects.create(
            dataset_import=dataset_import,
            row_number=row_number,
            source_department=dataset_import.source_department,
            accepted=not errors,
            original_data=original,
            normalized_data=normalized,
            validation_errors='; '.join(errors),
        )

    set_import_totals(
        dataset_import,
        total,
        accepted,
        rejected,
        error_messages,
    )


def process_geojson(dataset_import):
    dataset_import.source_file.seek(0)
    data = json.loads(dataset_import.source_file.read().decode('utf-8-sig'))

    if not isinstance(data, dict) or data.get('type') != 'FeatureCollection':
        raise ValidationError('GeoJSON must contain a top-level FeatureCollection.')

    features = data.get('features')
    if not isinstance(features, list):
        raise ValidationError('GeoJSON FeatureCollection must contain a features array.')

    total = accepted = rejected = 0
    error_messages = []

    crs = data.get('crs')
    crs_error = None
    if crs:
        crs_name = str(crs).lower()
        if '4326' not in crs_name and '84' not in crs_name:
            crs_error = 'Unsupported or unconfirmed coordinate reference system'

    for index, feature in enumerate(features, start=1):
        total += 1
        errors = []
        if crs_error:
            errors.append(crs_error)
        if not isinstance(feature, dict) or feature.get('type') != 'Feature':
            errors.append('Invalid GeoJSON Feature object')
            original = {}
            properties = {}
            geometry = None
        else:
            properties = feature.get('properties') or {}
            geometry = feature.get('geometry')
            original = {
                'properties': properties,
                'geometry': geometry,
            }
        if not isinstance(properties, dict):
            properties = {}

        parcel_id = properties.get('parcel_id')
        owner_name = properties.get('owner_name')
        if isinstance(parcel_id, str):
            parcel_id = parcel_id.strip()
        if isinstance(owner_name, str):
            owner_name = owner_name.strip()

        if not parcel_id:
            errors.append('Missing required value: parcel_id')
        if not owner_name:
            errors.append('Missing required value: owner_name')
        if not isinstance(geometry, dict):
            errors.append('Missing or invalid geometry')
        elif geometry.get('type') not in ('Polygon', 'MultiPolygon'):
            errors.append('Geometry must be a Polygon or MultiPolygon')
        elif not isinstance(geometry.get('coordinates'), list) or not geometry['coordinates']:
            errors.append('Geometry coordinates are missing')

        normalized = {
            'parcel_id': parcel_id or '',
            'owner_name': owner_name or '',
            'area_sqm': properties.get('area_sqm'),
            'zone': (
                properties.get('zone', '').strip()
                if isinstance(properties.get('zone'), str)
                else properties.get('zone', '')
            ),
            'geometry_type': geometry.get('type') if isinstance(geometry, dict) else None,
        }

        if errors:
            rejected += 1
            error_messages.append(f'Feature {index}: ' + '; '.join(errors))
        else:
            accepted += 1

        ImportedRecord.objects.create(
            dataset_import=dataset_import,
            row_number=index,
            source_department=dataset_import.source_department,
            accepted=not errors,
            original_data=original,
            normalized_data=normalized,
            validation_errors='; '.join(errors),
        )

    set_import_totals(
        dataset_import,
        total,
        accepted,
        rejected,
        error_messages,
    )


def set_import_totals(dataset_import, total, accepted, rejected, error_messages):
    dataset_import.total_records = total
    dataset_import.accepted_records = accepted
    dataset_import.rejected_records = rejected
    dataset_import.error_summary = '\n'.join(error_messages)

    if total == 0:
        dataset_import.processing_status = DatasetImport.STATUS_FAILED
    elif rejected:
        dataset_import.processing_status = DatasetImport.STATUS_COMPLETED_WITH_ERRORS
    else:
        dataset_import.processing_status = DatasetImport.STATUS_COMPLETED

    dataset_import.save()
