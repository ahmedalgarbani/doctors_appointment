from django.db import models
from django.contrib.auth import get_user_model
from doctors.models import Doctor, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from payments.models import HospitalPaymentMethod
from patients.models import Patients
from django.core.validators import MinLengthValidator
from django.utils import timezone
from notifications.models import Notifications
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


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

  

    payment_receipt = models.ImageField(
        upload_to='payment_receipts/',
        verbose_name="صورة سند الدفع",
        null=True,
        blank=False
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



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.booking.status = self.status
        self.booking.save()

        doctor_name = self.booking.doctor.user.get_full_name() if hasattr(self.booking.doctor, 'user') else str(self.booking.doctor)
        hospital_name = self.booking.hospital.name if self.booking.hospital else "المستشفى"

        day_display = self.booking.appointment_date.get_day_display() if hasattr(self.booking.appointment_date, 'get_day_display') else str(self.booking.appointment_date)

        appointment_time = self.booking.appointment_time
        if hasattr(appointment_time, 'start_time') and hasattr(appointment_time, 'end_time'):
            start = appointment_time.start_time.strftime('%I:%M %p').replace('AM', 'صباحًا').replace('PM', 'مساءً')
            end = appointment_time.end_time.strftime('%I:%M %p').replace('AM', 'صباحًا').replace('PM', 'مساءً')
            time_range = f"من {start} إلى {end}"
        else:
            time_range = str(appointment_time)

        booking_date = self.booking.booking_date

        if self.status == 'confirmed':
            message = _(
                f"✅ *تأكيد الحجز - {hospital_name}*\n\n"
                f"عزيزي العميل،\n"
                f"تم تأكيد حجزك مع الدكتور: *{doctor_name}*.\n"
                f"📅 التاريخ: {booking_date.strftime('%Y-%m-%d')}\n"
                f"🗓️ اليوم: {day_display}\n"
                f"⏰ الموعد: {time_range}\n\n"
                f"نتطلع لرؤيتك في {hospital_name}!"
            )
            notif_type = '2'

        elif self.status == 'completed':
            message = _(
                f"🎉 *تم إكمال الموعد - {hospital_name}*\n\n"
                f"عزيزي العميل،\n"
                f"انتهى موعدك مع الدكتور: *{doctor_name}*.\n"
                f"نتمنى لك دوام الصحة والعافية 🌟"
            )
            notif_type = '1'

        elif self.status == 'cancelled':
            message = _(
                f"❌ *إلغاء الحجز - {hospital_name}*\n\n"
                f"عزيزي العميل،\n"
                f"تم إلغاء حجزك مع الدكتور: *{doctor_name}*.\n"
                f"📅 التاريخ: {booking_date.strftime('%Y-%m-%d')}\n"
                f"🗓️ اليوم: {day_display}\n"
                f"⏰ الموعد: {time_range}\n"
                f"نأمل أن نراك قريبًا في {hospital_name} 🤝"
            )
            notif_type = '3'

        else:
            message = None

        if message:
            Notifications.objects.create(
                sender=self.created_by if self.created_by else None,
                user=self.booking.patient.user,
                message=message,
                notification_type=notif_type
            )


    @staticmethod
    def send_upcoming_appointment_notifications():
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)

        bookings = Booking.objects.filter(
            booking_date__in=[today, tomorrow],
            status='confirmed'
        )

        for booking in bookings:
            doctor_name = booking.doctor.user.get_full_name() if hasattr(booking.doctor, 'user') else str(booking.doctor)
            hospital_name = booking.hospital.name if booking.hospital else "المستشفى"
            patient_user = booking.patient.user

            day_display = booking.appointment_date.get_day_display() if hasattr(booking.appointment_date, 'get_day_display') else str(booking.appointment_date)

            appointment_time = booking.appointment_time
            if hasattr(appointment_time, 'start_time') and hasattr(appointment_time, 'end_time'):
                start = appointment_time.start_time.strftime('%I:%M %p').replace('AM', 'صباحًا').replace('PM', 'مساءً')
                end = appointment_time.end_time.strftime('%I:%M %p').replace('AM', 'صباحًا').replace('PM', 'مساءً')
                time_range = f"من {start} إلى {end}"
            else:
                time_range = str(appointment_time)

            if booking.booking_date == tomorrow:
                message = _(
                    f"🔔 *تذكير بموعد الغد - {hospital_name}*\n\n"
                    f"عزيزي العميل،\n"
                    f"نذكّرك أن لديك موعد غدًا مع الدكتور: *{doctor_name}*.\n"
                    f"🗓️ اليوم: {day_display}\n"
                    f"📅 التاريخ: {booking.booking_date}\n"
                    f"⏰ الموعد: {time_range}\n\n"
                    f"نتمنى لك وقتًا صحيًا ومميزًا في {hospital_name} 🌟"
                )
                notif_type = '4'

            elif booking.booking_date == today:
                message = _(
                    f"⏰ *موعدك اليوم - {hospital_name}*\n\n"
                    f"عزيزي العميل،\n"
                    f"لديك موعد اليوم مع الدكتور: *{doctor_name}*.\n"
                    f"📅 التاريخ: {booking.booking_date}\n"
                    f"🕒 الموعد: {time_range}\n\n"
                    f"يرجى الحضور في {hospital_name} في الوقت المحدد. نتمنى لك دوام الصحة 🌿"
                )
                notif_type = '5'

            else:
                continue

            Notifications.objects.create(
                sender=booking.hospital.admin_user if hasattr(booking.hospital, 'admin_user') else None,
                user=patient_user,
                message=message,
                notification_type=notif_type
            )
