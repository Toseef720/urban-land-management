from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import DatasetUploadForm
from .models import DatasetImport
from .services import process_dataset_import


class DatasetImportModelTests(TestCase):
    def test_creates_pending_import_with_zero_record_counts(self):
        uploaded_file = SimpleUploadedFile(
            'tax_records.csv',
            b'property_no,owner_name,address,tax_amount,tax_status',
            content_type='text/csv',
        )

        dataset_import = DatasetImport.objects.create(
            source_department=DatasetImport.DEPARTMENT_TAX,
            original_filename='tax_records.csv',
            file_format='CSV',
            source_file=uploaded_file,
        )

        self.assertEqual(dataset_import.processing_status, DatasetImport.STATUS_PENDING)
        self.assertEqual(dataset_import.total_records, 0)
        self.assertEqual(dataset_import.accepted_records, 0)
        self.assertEqual(dataset_import.rejected_records, 0)


class DatasetUploadFormTests(TestCase):
    def test_accepts_geojson_for_land_department(self):
        uploaded_file = SimpleUploadedFile(
            'land.geojson',
            b'{"type":"FeatureCollection","features":[]}',
            content_type='application/geo+json',
        )
        form = DatasetUploadForm(
            data={'source_department': DatasetImport.DEPARTMENT_LAND},
            files={'source_file': uploaded_file},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_accepts_csv_for_tax_department(self):
        uploaded_file = SimpleUploadedFile(
            'tax.csv',
            b'property_no,owner_name,address,tax_amount,tax_status',
            content_type='text/csv',
        )
        form = DatasetUploadForm(
            data={'source_department': DatasetImport.DEPARTMENT_TAX},
            files={'source_file': uploaded_file},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_accepts_csv_for_utility_department(self):
        uploaded_file = SimpleUploadedFile(
            'utility.csv',
            b'property_id,consumer_name,meter_id,address,utility_type',
            content_type='text/csv',
        )
        form = DatasetUploadForm(
            data={'source_department': DatasetImport.DEPARTMENT_UTILITY},
            files={'source_file': uploaded_file},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_csv_for_land_department(self):
        uploaded_file = SimpleUploadedFile(
            'land.csv',
            b'parcel_id,owner_name',
            content_type='text/csv',
        )
        form = DatasetUploadForm(
            data={'source_department': DatasetImport.DEPARTMENT_LAND},
            files={'source_file': uploaded_file},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('source_file', form.errors)


class DatasetProcessingTests(TestCase):
    def test_processes_utility_csv_rows(self):
        uploaded_file = SimpleUploadedFile(
            'utility.csv',
            (
                b'property_id,consumer_name,meter_id,address,utility_type\n'
                b'P-001,Aisha Khan,MTR-1001,12 Garden Road,Electric\n'
                b'P-002,Bilal Ahmed,,5 Cedar Avenue,Water\n'
            ),
            content_type='text/csv',
        )
        dataset_import = DatasetImport.objects.create(
            source_department=DatasetImport.DEPARTMENT_UTILITY,
            original_filename='utility.csv',
            file_format='CSV',
            source_file=uploaded_file,
        )

        process_dataset_import(dataset_import)

        dataset_import.refresh_from_db()
        self.assertEqual(dataset_import.total_records, 2)
        self.assertEqual(dataset_import.accepted_records, 1)
        self.assertEqual(dataset_import.rejected_records, 1)
        self.assertEqual(dataset_import.records.first().normalized_data['meter_id'], 'MTR-1001')
    def test_processes_valid_and_invalid_csv_rows(self):
        uploaded_file = SimpleUploadedFile(
            'tax.csv',
            (
                b'property_no,owner_name,address,tax_amount,tax_status\n'
                b'TAX-001,Test Owner,Test Address,100,Paid\n'
                b',Missing Owner,,50,Due\n'
            ),
            content_type='text/csv',
        )
        dataset_import = DatasetImport.objects.create(
            source_department=DatasetImport.DEPARTMENT_TAX,
            original_filename='tax.csv',
            file_format='CSV',
            source_file=uploaded_file,
        )

        process_dataset_import(dataset_import)

        dataset_import.refresh_from_db()
        self.assertEqual(dataset_import.total_records, 2)
        self.assertEqual(dataset_import.accepted_records, 1)
        self.assertEqual(dataset_import.rejected_records, 1)
        self.assertEqual(
            dataset_import.processing_status,
            DatasetImport.STATUS_COMPLETED_WITH_ERRORS,
        )
        self.assertEqual(dataset_import.records.count(), 2)

    def test_processes_valid_geojson_feature_collection(self):
        uploaded_file = SimpleUploadedFile(
            'land.geojson',
            (
                b'{"type":"FeatureCollection","features":[{"type":"Feature",'
                b'"properties":{"parcel_id":"P-001","owner_name":"Test Owner",'
                b'"area_sqm":100,"zone":"A"},"geometry":{"type":"Polygon",'
                b'"coordinates":[[[0,0],[1,0],[1,1],[0,0]]]}}]}'
            ),
            content_type='application/geo+json',
        )
        dataset_import = DatasetImport.objects.create(
            source_department=DatasetImport.DEPARTMENT_LAND,
            original_filename='land.geojson',
            file_format='GEOJSON',
            source_file=uploaded_file,
        )

        process_dataset_import(dataset_import)

        dataset_import.refresh_from_db()
        self.assertEqual(dataset_import.total_records, 1)
        self.assertEqual(dataset_import.accepted_records, 1)
        self.assertEqual(dataset_import.rejected_records, 0)
        self.assertEqual(dataset_import.records.first().normalized_data['parcel_id'], 'P-001')

    def test_rejects_empty_file(self):
        uploaded_file = SimpleUploadedFile(
            'tax.csv',
            b'',
            content_type='text/csv',
        )
        form = DatasetUploadForm(
            data={'source_department': DatasetImport.DEPARTMENT_TAX},
            files={'source_file': uploaded_file},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('source_file', form.errors)
