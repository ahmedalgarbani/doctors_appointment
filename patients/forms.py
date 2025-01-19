from django import forms
from .models import Patients

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = [
            'birth_date', 'gender', 'weight', 'height', 'age', 'blood_group', 'notes'
        ]
