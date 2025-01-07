from django import forms
from .models import Patients

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = ['full_name', 'birth_date', 'gender', 'address', 'phone_number', 'email', 'profile_picture', 'notes']
