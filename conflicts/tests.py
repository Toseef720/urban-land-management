from django.test import TestCase
from django.urls import reverse

from datasets.models import DatasetImport, ImportedRecord
from harmonization.models import HarmonizedRecord
from properties.models import Property
from standardization.models import StandardizationResult

from .models import Conflict, ConflictValue
from .services import detect_conflicts


class DetectConflictsTests(TestCase):
    def setUp(self):
        self.property = Property.objects.create(
            parcel_id='P-100',
            property_name='Test property',
            owner_name='Original owner',
            address='Original address',
            area=100,
        )

    def add_record(self, department, data):
        dataset_import = DatasetImport.objects.create(
            source_department=department,
            original_filename=f'{department}.csv',
            file_format='CSV',
            source_file='',
        )
        imported_record = ImportedRecord.objects.create(
            dataset_import=dataset_import,
            row_number=1,
            source_department=department,
            accepted=True,
            normalized_data={},
        )
        result = StandardizationResult.objects.create(
            source_record=imported_record,
            standardized_data=data,
            is_valid=True,
        )
        HarmonizedRecord.objects.create(
            standardization_result=result,
            property=self.property,
            match_status=HarmonizedRecord.STATUS_MATCHED,
        )
        return result

    def test_detects_mismatches_only_between_departments_and_matching_roles(self):
        self.add_record(
            DatasetImport.DEPARTMENT_LAND,
            {
                'person_name': 'Alex One',
                'name_role': 'owner',
                'land_area_sqm': 100,
            },
        )
        self.add_record(
            DatasetImport.DEPARTMENT_TAX,
            {
                'person_name': 'Alex Two',
                'name_role': 'owner',
                'address': 'Street A',
            },
        )
        self.add_record(
            DatasetImport.DEPARTMENT_UTILITY,
            {
                'person_name': 'Utility Customer',
                'name_role': 'consumer',
                'address': 'Street B',
            },
        )

        result = detect_conflicts()

        conflicts = list(Conflict.objects.order_by('field_name'))
        person_conflict = Conflict.objects.get(
            field_name=Conflict.FIELD_PERSON_NAME,
        )
        self.assertEqual(result['created'], 2)
        self.assertEqual(
            [conflict.field_name for conflict in conflicts],
            [Conflict.FIELD_ADDRESS, Conflict.FIELD_PERSON_NAME],
        )
        self.assertEqual(
            conflicts[0].values.count(),
            2,
        )
        self.assertEqual(person_conflict.values.count(), 2)
        self.assertEqual(
            set(person_conflict.values.values_list(
                'standardization_result__source_record__source_department',
                flat=True,
            )),
            {DatasetImport.DEPARTMENT_LAND, DatasetImport.DEPARTMENT_TAX},
        )

    def test_repeated_scans_are_idempotent_and_clear_disappeared_conflicts(self):
        land_result = self.add_record(
            DatasetImport.DEPARTMENT_LAND,
            {
                'person_name': 'Alex One',
                'name_role': 'owner',
            },
        )
        tax_result = self.add_record(
            DatasetImport.DEPARTMENT_TAX,
            {
                'person_name': 'Alex Two',
                'name_role': 'owner',
            },
        )

        first_scan = detect_conflicts()
        second_scan = detect_conflicts()
        conflict = Conflict.objects.get(field_name=Conflict.FIELD_PERSON_NAME)

        self.assertEqual(first_scan['created'], 1)
        self.assertEqual(second_scan['created'], 0)
        self.assertEqual(Conflict.objects.count(), 1)
        self.assertEqual(conflict.status, Conflict.STATUS_PENDING)

        tax_result.standardized_data['person_name'] = 'Alex One'
        tax_result.save(update_fields=['standardized_data'])
        clearing_scan = detect_conflicts()
        conflict.refresh_from_db()

        self.assertEqual(clearing_scan['cleared'], 1)
        self.assertEqual(conflict.status, Conflict.STATUS_CLEARED)

        tax_result.standardized_data['person_name'] = 'Alex Two'
        tax_result.save(update_fields=['standardized_data'])
        reactivation_scan = detect_conflicts()
        conflict.refresh_from_db()

        self.assertEqual(reactivation_scan['created'], 0)
        self.assertEqual(reactivation_scan['reactivated'], 1)
        self.assertEqual(conflict.status, Conflict.STATUS_PENDING)
        self.assertEqual(conflict.values.count(), 2)
        self.assertEqual(land_result.id, conflict.values.get(
            standardization_result=land_result,
        ).standardization_result_id)


class ConflictDashboardTests(TestCase):
    def setUp(self):
        self.property = Property.objects.create(
            parcel_id='P-200',
            property_name='Dashboard property',
            owner_name='Owner',
            address='Main Street',
            area=75,
        )

    def log_in(self):
        session = self.client.session
        session['demo_logged_in'] = True
        session.save()

    def add_source_value(self, department):
        dataset_import = DatasetImport.objects.create(
            source_department=department,
            original_filename=f'{department}.csv',
            file_format='CSV',
            source_file='',
        )
        imported_record = ImportedRecord.objects.create(
            dataset_import=dataset_import,
            row_number=1,
            source_department=department,
            accepted=True,
        )
        result = StandardizationResult.objects.create(
            source_record=imported_record,
            standardized_data={},
            is_valid=True,
        )
        return result

    def test_dashboard_redirects_when_not_logged_in(self):
        response = self.client.get(reverse('conflict_dashboard'))

        self.assertRedirects(
            response,
            reverse('login'),
            fetch_redirect_response=False,
        )

    def test_post_runs_detection_and_reports_result(self):
        self.log_in()

        response = self.client.post(
            reverse('conflict_dashboard'),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Detection complete: 0 new, 0 reactivated, 0 cleared, 0 active conflicts.',
        )

    def test_dashboard_shows_counts_values_and_details_action(self):
        self.log_in()
        conflict = Conflict.objects.create(
            property=self.property,
            field_name=Conflict.FIELD_PERSON_NAME,
            snapshot_key='a' * 64,
        )
        land_result = self.add_source_value(DatasetImport.DEPARTMENT_LAND)
        tax_result = self.add_source_value(DatasetImport.DEPARTMENT_TAX)
        ConflictValue.objects.create(
            conflict=conflict,
            standardization_result=land_result,
            value_snapshot='Owner A',
        )
        ConflictValue.objects.create(
            conflict=conflict,
            standardization_result=tax_result,
            value_snapshot='Owner B',
        )
        Conflict.objects.create(
            property=self.property,
            field_name=Conflict.FIELD_ADDRESS,
            snapshot_key='b' * 64,
            status=Conflict.STATUS_RESOLVED,
        )
        Conflict.objects.create(
            property=self.property,
            field_name=Conflict.FIELD_LAND_AREA_SQM,
            snapshot_key='c' * 64,
            status=Conflict.STATUS_CLEARED,
        )

        response = self.client.get(reverse('conflict_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['counts']['total'], 3)
        self.assertEqual(response.context['counts']['pending'], 1)
        self.assertEqual(response.context['counts']['resolved'], 1)
        self.assertEqual(response.context['counts']['cleared'], 1)
        self.assertContains(response, 'Land Department')
        self.assertContains(response, 'Property Tax Department')
        self.assertContains(response, 'View details')
        self.assertContains(response, 'Conflicts by field')

    def test_detail_compares_department_values_side_by_side(self):
        self.log_in()
        conflict = Conflict.objects.create(
            property=self.property,
            field_name=Conflict.FIELD_PERSON_NAME,
            snapshot_key='d' * 64,
        )
        land_result = self.add_source_value(DatasetImport.DEPARTMENT_LAND)
        tax_result = self.add_source_value(DatasetImport.DEPARTMENT_TAX)
        ConflictValue.objects.create(
            conflict=conflict,
            standardization_result=land_result,
            value_snapshot='Owner A',
        )
        ConflictValue.objects.create(
            conflict=conflict,
            standardization_result=tax_result,
            value_snapshot='Owner B',
        )

        response = self.client.get(
            reverse('conflict_detail', kwargs={'conflict_id': conflict.id}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Land Department')
        self.assertContains(response, 'Property Tax Department')
        self.assertContains(response, 'Utility Department')
        self.assertContains(response, 'Owner A')
        self.assertContains(response, 'Owner B')
        self.assertContains(response, 'Not available')

    def test_resolution_saves_selected_value_without_changing_source_data(self):
        self.log_in()
        conflict = Conflict.objects.create(
            property=self.property,
            field_name=Conflict.FIELD_PERSON_NAME,
            snapshot_key='e' * 64,
        )
        land_result = self.add_source_value(DatasetImport.DEPARTMENT_LAND)
        tax_result = self.add_source_value(DatasetImport.DEPARTMENT_TAX)
        land_value = ConflictValue.objects.create(
            conflict=conflict,
            standardization_result=land_result,
            value_snapshot='Owner A',
        )
        tax_value = ConflictValue.objects.create(
            conflict=conflict,
            standardization_result=tax_result,
            value_snapshot='Owner B',
        )

        response = self.client.post(
            reverse('resolve_conflict', kwargs={'conflict_id': conflict.id}),
            {
                'source_value': str(tax_value.id),
                'corrected_value': '',
                'resolution_note': 'Verified against the signed record.',
            },
        )

        conflict.refresh_from_db()
        self.property.refresh_from_db()
        land_value.refresh_from_db()
        tax_value.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('conflict_detail', kwargs={'conflict_id': conflict.id}),
            fetch_redirect_response=False,
        )
        self.assertEqual(conflict.status, Conflict.STATUS_RESOLVED)
        self.assertEqual(conflict.resolution.resolved_value, 'Owner B')
        self.assertEqual(
            conflict.resolution.resolution_note,
            'Verified against the signed record.',
        )
        self.assertEqual(self.property.owner_name, 'Owner')
        self.assertEqual(land_value.value_snapshot, 'Owner A')
        self.assertEqual(tax_value.value_snapshot, 'Owner B')
        detail_response = self.client.get(
            reverse('conflict_detail', kwargs={'conflict_id': conflict.id}),
        )
        self.assertContains(detail_response, 'Owner B')
        self.assertContains(
            detail_response,
            'Verified against the signed record.',
        )

    def test_resolution_accepts_a_corrected_value(self):
        self.log_in()
        conflict = Conflict.objects.create(
            property=self.property,
            field_name=Conflict.FIELD_ADDRESS,
            snapshot_key='f' * 64,
        )

        response = self.client.post(
            reverse('resolve_conflict', kwargs={'conflict_id': conflict.id}),
            {
                'source_value': '',
                'corrected_value': 'Verified address',
                'resolution_note': 'Confirmed by the land office.',
            },
        )

        self.assertRedirects(
            response,
            reverse('conflict_detail', kwargs={'conflict_id': conflict.id}),
            fetch_redirect_response=False,
        )
        conflict.refresh_from_db()
        self.assertEqual(conflict.status, Conflict.STATUS_RESOLVED)
        self.assertEqual(
            conflict.resolution.resolved_value,
            'Verified address',
        )
