from django import forms
from .models import Property


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'parcel_id',
            'property_name',
            'owner_name',
            'address',
            'area',
            'description',
            'photo'
        ]
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 3
            }),
            'description': forms.Textarea(attrs={
                'rows': 3
            })
        }