from django import forms
from .models import Specialties, Doctors, DoctorRates, DoctorSchedules

#a
class SpecialtiesForm(forms.ModelForm):
    class Meta:
        model = Specialties
        fields = '__all__'


class DoctorsForm(forms.ModelForm):
    class Meta:
        model = Doctors
        fields = '__all__'


class DoctorRatesForm(forms.ModelForm):
    class Meta:
        model = DoctorRates
        fields = '__all__'


class DoctorSchedulesForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedules
        fields = '__all__'
