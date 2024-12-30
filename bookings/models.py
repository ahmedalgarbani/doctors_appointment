from django.db import models
from django.contrib.auth import get_user_model
from doctors.models import Doctor, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from patients.models import Patients
from doctors.models import Doctor
from django.utils.translation import gettext_lazy as _  # إضافة هذا السطر

User = get_user_model()

class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    PURPOSE_CHOICES = [
        ('consultation', _('استشارة')),
        ('surgery', _('جراحة')),
        ('checkup', _('فحص دوري')),
        ('emergency', _('طوارئ')),
    ]

    TYPE_CHOICES = [
        ('new', _('جديد')),
        ('followup', _('متابع')),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='hospitals')
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name='bookings')
    appointment_date = models.ForeignKey(DoctorSchedules, on_delete=models.CASCADE, related_name='date')
    appointment_time = models.ForeignKey(DoctorShifts, on_delete=models.CASCADE, related_name='time')
    is_online = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("المبلغ"))
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, verbose_name=_("الغرض"))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_("نوع الحجز"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def __str__(self):
        return f"{self.patient.get_full_name()} - Dr. {self.doctor.full_name} - {self.appointment_date}"
