from django import forms
from .models import Specialty, Doctor, DoctorSchedules

#a
class SpecialtiesForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = '__all__'


class DoctorsForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'





class DoctorSchedulesForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedules
        fields = '__all__'







