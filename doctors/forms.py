
from django import forms
from .models import Specialties, Doctors, DoctorRates, DoctorSchedules

#ahmed
class SpecialtiesForm(forms.ModelForm):
    class Meta:
        model = Specialties
        fields = ['specialty_name']

class DoctorsForm(forms.ModelForm):
    class Meta:
        model = Doctors
        fields = ['name',  'specialty_id']

class DoctorRatesForm(forms.ModelForm):
    class Meta:
        model = DoctorRates
        fields = ['doctor_id', 'rate']

class DoctorSchedulesForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedules
        fields = ['doctor_id',  'day', 'start_time', 'end_time']
