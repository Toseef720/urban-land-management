import hashlib
import json

from django.db import transaction

from harmonization.models import HarmonizedRecord

from .models import Conflict, ConflictValue


FIELD_KEYS = (
    (Conflict.FIELD_PERSON_NAME, 'person_name', 'name_role'),
    (Conflict.FIELD_ADDRESS, 'address', None),
    (Conflict.FIELD_LAND_AREA_SQM, 'land_area_sqm', None),
)


def _normalize_value(value):
    if value is None:
        return ''
    return ' '.join(str(value).strip().split()).casefold()


def _snapshot_key(property_id, field_name, role, entries):
    values = [
        {
            'department': department,
            'result_id': result.id,
            'value': value,
        }
        for result, department, value in entries
    ]
    values.sort(key=lambda item: (item['department'], item['result_id']))
    payload = {
        'property_id': property_id,
        'field_name': field_name,
        'role': role,
        'values': values,
    }
    encoded = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def _get_conflicting_groups(records, data_key, role_key):
    groups = {}
    for result, department in records:
        data = result.standardized_data
        if not isinstance(data, dict):
            continue

        value = data.get(data_key)
        if not _normalize_value(value):
            continue

        role = None
        if role_key:
            role = _normalize_value(data.get(role_key))
            if not role:
                continue

        groups.setdefault(role, []).append((result, department, value))

    return [
        (role, entries)
        for role, entries in groups.items()
        if len({department for _, department, _ in entries}) > 1
        and len({_normalize_value(value) for _, _, value in entries}) > 1
    ]


@transaction.atomic
def detect_conflicts():
    harmonized_records = HarmonizedRecord.objects.filter(
        match_status=HarmonizedRecord.STATUS_MATCHED,
        property__isnull=False,
        standardization_result__is_valid=True,
        standardization_result__source_record__accepted=True,
    ).select_related(
        'property',
        'standardization_result',
        'standardization_result__source_record',
    )

    records_by_property = {}
    for harmonized_record in harmonized_records:
        result = harmonized_record.standardization_result
        department = result.source_record.source_department
        records_by_property.setdefault(
            harmonized_record.property,
            [],
        ).append((result, department))

    current_snapshot_keys = set()
    created_count = 0
    reactivated_count = 0

    for property_obj, records in records_by_property.items():
        for field_name, data_key, role_key in FIELD_KEYS:
            for role, entries in _get_conflicting_groups(
                records,
                data_key,
                role_key,
            ):
                snapshot_key = _snapshot_key(
                    property_obj.id,
                    field_name,
                    role,
                    entries,
                )
                conflict, created = Conflict.objects.get_or_create(
                    snapshot_key=snapshot_key,
                    defaults={
                        'property': property_obj,
                        'field_name': field_name,
                        'status': Conflict.STATUS_PENDING,
                    },
                )
                current_snapshot_keys.add(snapshot_key)

                if created:
                    created_count += 1
                    for result, _, value in entries:
                        ConflictValue.objects.create(
                            conflict=conflict,
                            standardization_result=result,
                            value_snapshot=value,
                        )
                elif conflict.status == Conflict.STATUS_CLEARED:
                    conflict.status = Conflict.STATUS_PENDING
                    conflict.save(update_fields=['status'])
                    reactivated_count += 1

    cleared_count = Conflict.objects.filter(
        status=Conflict.STATUS_PENDING,
    ).exclude(
        snapshot_key__in=current_snapshot_keys,
    ).update(status=Conflict.STATUS_CLEARED)

    return {
        'created': created_count,
        'reactivated': reactivated_count,
        'cleared': cleared_count,
        'active': len(current_snapshot_keys),
    }
