from django.db import models
from django.contrib.auth import get_user_model
from doctors.models import Doctor, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from payments.models import HospitalPaymentMethod
from patients.models import Patients
from django.core.validators import MinLengthValidator

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'معلق'),
        ('confirmed', 'مؤكد'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي')
    ]
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="الطبيب"
    )
    patient = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="المريض"
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='hospital_bookings',
        verbose_name="المستشفى"
    )
    appointment_date = models.ForeignKey(
        DoctorSchedules,
        on_delete=models.CASCADE,
        related_name='date',
        verbose_name="اليوم"
    )
    appointment_time = models.ForeignKey(
        DoctorShifts,
        on_delete=models.CASCADE,
        related_name='time',
        verbose_name="الموعد"
    )
    booking_date = models.DateField(verbose_name="تاريخ الحجز")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="المبلغ"
    )
    is_online = models.BooleanField(default=False, verbose_name="استشارة عن بعد")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="الحالة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    # حقول الدفع
    payment_method = models.ForeignKey(
        HospitalPaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings',
        verbose_name="طريقة الدفع"
    )
    transfer_number = models.CharField(
    max_length=50, 
    blank=True, 
    null=True, 
    verbose_name="رقم الحوالة",
    validators=[MinLengthValidator(5, 'رقم الحوالة يجب أن يكون 5 أرقام على الأقل')]
)
    payment_verified = models.BooleanField(default=False, verbose_name="تم التحقق من الدفع")
    payment_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ التحقق من الدفع"
    )
    payment_verified_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_bookings',
        verbose_name="تم التحقق بواسطة"
    )
    payment_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات الدفع"
    )
    
    account_image = models.ImageField(
        upload_to='booking_images/',
        verbose_name="صورة سند الحساب",
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.booking_date}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"
        
    def save(self, *args, **kwargs):
        # إذا تم التحقق من الدفع، قم بتحديث حالة الحجز إلى مؤكد
        if self.payment_verified and self.status == 'pending':
            self.status = 'confirmed'
        super().save(*args, **kwargs)

class BookingStatusHistory(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name="الحجز"
    )
    status = models.CharField(
        max_length=20,
        choices=Booking.STATUS_CHOICES,
        verbose_name="الحالة"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات"
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='booking_status_updates',
        verbose_name="تم التحديث بواسطة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التحديث")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "سجل حالة الحجز"
        verbose_name_plural = "سجلات حالات الحجوزات"

    def __str__(self):
        return f"{self.booking} - {self.status} - {self.created_at}"
