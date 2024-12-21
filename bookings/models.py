from django.db import models
from doctors_appointment import settings
from hospitals.models import BaseModel
from django.utils.translation import gettext_lazy as _

class Booking(BaseModel): 
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

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_bookings'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='doctor_bookings'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='hospital_bookings'
    )
    date = models.DateField()
    time = models.TimeField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("المبلغ")
    )
    status = models.ForeignKey(
        'bookings.BookingStatus',
        on_delete=models.CASCADE,
        verbose_name=_("حالة الحجز"),
        related_name='bookings'
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("حجز")
        verbose_name_plural = _("الحجوزات")
        ordering = ['-date', '-time']

    def __str__(self):
        return f"Booking: {self.patient} with {self.doctor} on {self.date}"


class BookingStatus(BaseModel):  
    booking_status_name = models.CharField(
        max_length=50,
        verbose_name=_("اسم الحالة")
    )
    status_code = models.IntegerField(
        verbose_name=_("رمز الحالة"),
        unique=True
    )

    class Meta:
        verbose_name = _("حالة الحجز")
        verbose_name_plural = _("حالات الحجز")
        ordering = ['status_code']

    def __str__(self):
        return f"{self.booking_status_name} ({self.status_code})"

# Create your models here.
