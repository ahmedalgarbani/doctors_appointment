from django.db import models
from django.contrib.auth import get_user_model
from doctors.models import Doctor

User = get_user_model()

<<<<<<< HEAD
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
=======
class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    is_online = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
>>>>>>> 17a6cc346d6933bc45c5346f29d0bec0ec6e5923

    def __str__(self):
        return f"{self.patient.get_full_name()} - Dr. {self.doctor.full_name} - {self.appointment_date}"
