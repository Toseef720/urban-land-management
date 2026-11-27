from standardization.models import StandardizationResult
from properties.models import Property
from .models import HarmonizedRecord
from datasets.models import DatasetImport
from properties.models import Property
from standardization.models import StandardizationResult


def harmonize_record(result):
    """
    Match one standardized record with an existing master property.
    """

    # Invalid standardized records cannot be matched.
    if not result.is_valid:
        HarmonizedRecord.objects.update_or_create(
            standardization_result=result,
            defaults={
                'property': None,
                'match_status': HarmonizedRecord.STATUS_INVALID,
                'match_method': '',
            }
        )
        return 'invalid'

    standardized_data = result.standardized_data

    property_id = standardized_data.get('property_id', '').strip()

    # Search for an exact property ID match.
    master_property = Property.objects.filter(
        parcel_id__iexact=property_id
    ).first()

    if master_property:
        HarmonizedRecord.objects.update_or_create(
            standardization_result=result,
            defaults={
                'property': master_property,
                'match_status': HarmonizedRecord.STATUS_MATCHED,
                'match_method': 'Exact Property ID',
            }
        )
        return 'matched'

    # No matching property found.
    HarmonizedRecord.objects.update_or_create(
        standardization_result=result,
        defaults={
            'property': None,
            'match_status': HarmonizedRecord.STATUS_UNMATCHED,
            'match_method': '',
        }
    )

    return 'unmatched'


def harmonize_all_records():
    """
    Harmonize all standardized records.
    """

    results = StandardizationResult.objects.all()

    counts = {
        'matched': 0,
        'unmatched': 0,
        'invalid': 0,
    }

    for result in results:
        status = harmonize_record(result)
        counts[status] += 1

    return counts

def create_master_properties_from_land_records():

    land_records = StandardizationResult.objects.filter(
        source_record__source_department=DatasetImport.DEPARTMENT_LAND,
        is_valid=True
    )

    created = 0
    existing = 0

    for record in land_records:

        data = record.standardized_data

        property_id = data.get('property_id')

        if not property_id:
            continue

        property_obj, was_created = Property.objects.get_or_create(
            parcel_id=property_id,
            defaults={
                'property_name': f"Property {property_id}",
                'owner_name': data.get('person_name', ''),
                'address': '',
                'area': float(data.get('land_area_sqm') or 0),
                'description': (
                    f"Zone: {data.get('zone', '')}; "
                    f"Geometry: {data.get('geometry_type', '')}"
                )
            }
        )

        if was_created:
            created += 1
        else:
            existing += 1

    return {
        'created': created,
        'existing': existing
    }