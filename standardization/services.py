
from datasets.models import DatasetImport, ImportedRecord
from .models import StandardizationResult
from decimal import Decimal, InvalidOperation


def clean_text(value):
    """Remove extra spaces while preserving the original letter casing."""
    if value is None:
        return ''

    return ' '.join(str(value).strip().split())


def standardize_record(record):
    """Convert an accepted imported record into a common data structure."""

    data = record.normalized_data
    department = record.source_department

    standardized = {
        'property_id': '',
        'person_name': '',
        'name_role': '',
        'address': '',
    }

    if department == DatasetImport.DEPARTMENT_LAND:
        standardized.update({
            'property_id': clean_text(data.get('parcel_id')),
            'person_name': clean_text(data.get('owner_name')),
            'name_role': 'owner',
            'land_area_sqm': data.get('area_sqm'),
            'zone': clean_text(data.get('zone')),
            'geometry_type': clean_text(data.get('geometry_type')),
        })

    elif department == DatasetImport.DEPARTMENT_TAX:
        standardized.update({
            'property_id': clean_text(data.get('property_no')),
            'person_name': clean_text(data.get('owner_name')),
            'name_role': 'owner',
            'address': clean_text(data.get('address')),
            'tax_amount': clean_text(data.get('tax_amount')),
            'tax_status': clean_text(data.get('tax_status')),
        })

    elif department == DatasetImport.DEPARTMENT_UTILITY:
        standardized.update({
            'property_id': clean_text(data.get('property_id')),
            'person_name': clean_text(data.get('consumer_name')),
            'name_role': 'consumer',
            'address': clean_text(data.get('address')),
            'meter_id': clean_text(data.get('meter_id')),
            'utility_type': clean_text(data.get('utility_type')),
        })

    else:
        raise ValueError(f'Unsupported department: {department}')

    errors = validate_standardized_data(
        standardized,
        department
    )

    result, created = StandardizationResult.objects.update_or_create(
        source_record=record,
        defaults={
            'standardized_data': standardized,
            'is_valid': len(errors) == 0,
            'errors': '\n'.join(errors),
        }
    )

    return result


def standardize_dataset(dataset_import):
    """Standardize all accepted records belonging to one dataset import."""

    records = ImportedRecord.objects.filter(
        dataset_import=dataset_import,
        accepted=True,
    )

    processed = 0

    for record in records:
        standardize_record(record)
        processed += 1

    return processed





def validate_standardized_data(data, department):
    errors = []

    # Common required fields
    required_fields = {
        'property_id': 'Property ID',
        'person_name': 'Person name',
    }

    if department in (
        DatasetImport.DEPARTMENT_TAX,
        DatasetImport.DEPARTMENT_UTILITY,
    ):
        required_fields['address'] = 'Address'

    if department == DatasetImport.DEPARTMENT_UTILITY:
        required_fields.update({
            'meter_id': 'Meter ID',
            'utility_type': 'Utility type',
        })

    for field, label in required_fields.items():
        if not clean_text(data.get(field)):
            errors.append(f'{label} is required.')

    # Land-specific validation
    if department == DatasetImport.DEPARTMENT_LAND:
        area = data.get('land_area_sqm')

        try:
            if area is None or Decimal(str(area)) <= 0:
                errors.append('Land area must be greater than zero.')
        except (InvalidOperation, ValueError, TypeError):
            errors.append('Land area must be a valid number.')

        geometry = data.get('geometry_type')

        if geometry not in ('Polygon', 'MultiPolygon'):
            errors.append('Invalid land geometry type.')

    # Tax-specific validation
    if department == DatasetImport.DEPARTMENT_TAX:
        tax_amount = data.get('tax_amount')

        if tax_amount not in (None, ''):
            try:
                if Decimal(str(tax_amount)) < 0:
                    errors.append('Tax amount cannot be negative.')
            except (InvalidOperation, ValueError, TypeError):
                errors.append('Tax amount must be a valid number.')

    return errors
