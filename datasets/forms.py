from django import forms

from .models import DatasetImport


class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = DatasetImport
        fields = ['source_department', 'source_file']
        labels = {
            'source_department': 'Source department',
            'source_file': 'Dataset file',
        }

    def clean_source_file(self):
        uploaded_file = self.cleaned_data['source_file']
        department = self.cleaned_data.get('source_department')
        filename = uploaded_file.name.lower()

        if department == DatasetImport.DEPARTMENT_LAND:
            if not filename.endswith('.geojson'):
                raise forms.ValidationError(
                    'The Land Department requires a GeoJSON (.geojson) file.'
                )
        else:
            if not filename.endswith('.csv'):
                raise forms.ValidationError(
                    'Property Tax and Utility departments require a CSV (.csv) file.'
                )

        if uploaded_file.size == 0:
            raise forms.ValidationError('The uploaded file is empty.')

        return uploaded_file
