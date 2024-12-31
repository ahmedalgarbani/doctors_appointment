from django.db import models
from doctors_appointment import settings
from hospitals.models import BaseModel
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from doctors.models import Doctor, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from patients.models import Patients

User = get_user_model()

class Booking(models.Model):
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

    BOOKING_STATUS = (
        ('0', 'Pending'),
        ('1', 'Confirmed'),
        ('2', 'Completed'),
        ('3', 'Cancelled'),
    )

    patient = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='hospital_bookings'
    )
    appointment_date = models.ForeignKey(
        DoctorSchedules,
        on_delete=models.CASCADE,
        related_name='date'
    )
    appointment_time = models.ForeignKey(
        DoctorShifts,
        on_delete=models.CASCADE,
        related_name='time'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("المبلغ")
    )
    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
        verbose_name=_("الغرض")
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_("نوع الحجز")
    )
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='0',
        verbose_name=_("حالة الحجز")
    )
    is_online = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("حجز")
        verbose_name_plural = _("الحجوزات")
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"Booking: {self.patient} with {self.doctor} on {self.appointment_date}"
