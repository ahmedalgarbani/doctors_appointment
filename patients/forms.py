from django import forms
from .models import Patients

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = [
            'birth_date', 'gender', 'weight', 'height', 'age', 'blood_group', 'notes'
        ]

from django import forms
from bookings.models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'appointment_date', 'appointment_time', 'payment_method', 'transfer_number']
