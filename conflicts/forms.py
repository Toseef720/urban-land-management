from django import forms

from datasets.models import DatasetImport


class ConflictResolutionForm(forms.Form):
    source_value = forms.ChoiceField(
        choices=[('', 'Select a reported value')],
        required=False,
        label='Reported value',
    )
    corrected_value = forms.CharField(
        required=False,
        strip=True,
        label='Corrected value',
    )
    resolution_note = forms.CharField(
        strip=True,
        label='Resolution note',
        widget=forms.Textarea(attrs={'rows': 4}),
    )

    def __init__(self, *args, conflict, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select a reported value')]
        self.source_values = {}

        values = conflict.values.select_related(
            'standardization_result__source_record__dataset_import',
        )
        for item in values:
            source_id = str(item.pk)
            department = (
                item.standardization_result.source_record.dataset_import
                .get_source_department_display()
            )
            value = str(item.value_snapshot)
            choices.append((source_id, f'{department}: {value}'))
            self.source_values[source_id] = value

        self.fields['source_value'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        source_value = cleaned_data.get('source_value')
        corrected_value = cleaned_data.get('corrected_value')

        if source_value and corrected_value:
            self.add_error(
                'corrected_value',
                'Choose a reported value or enter a correction, not both.',
            )
        elif source_value:
            cleaned_data['resolved_value'] = self.source_values[source_value]
        elif corrected_value:
            cleaned_data['resolved_value'] = corrected_value
        else:
            self.add_error(
                'corrected_value',
                'Select a reported value or enter a corrected value.',
            )

        return cleaned_data
