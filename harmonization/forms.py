
from django import forms
from properties.models import Property


class ManualMatchForm(forms.Form):

    property = forms.ModelChoiceField(
        queryset=Property.objects.all().order_by('parcel_id'),
        label="Select Master Property",
        empty_label="Choose a property",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
