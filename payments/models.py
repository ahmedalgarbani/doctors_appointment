import datetime
from django.db import models
from hospitals.models import BaseModel, Hospital
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.translation import gettext_lazy as _
    
from notifications.models import Notifications



# ------------PaymentOption-------------
class PaymentOption(models.Model):
    method_name = models.CharField(max_length=100, verbose_name=_("اسم طريقة الدفع"))
    logo = models.ImageField(upload_to='payment_logos/', null=True, blank=True, verbose_name=_("شعار"))
    currency = models.CharField(max_length=25, default='RYL', verbose_name=_("العملة"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    
    def __str__(self):
        status = _("مفعّل") if self.is_active else _("معطّل")
        return f"{self.method_name} - {self.currency} ({status})"
    
    class Meta:
        verbose_name = _("طريقة دفع")
        verbose_name_plural = _("طرق الدفع")

# ------------HospitalPaymentMethod-------------
class HospitalPaymentMethod(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='hospital_payment_methods', verbose_name=_("المستشفى"))
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE, verbose_name=_("طريقة الدفع"))
    account_name = models.CharField(max_length=100, verbose_name=_("اسم الحساب"))
    account_number = models.CharField(max_length=50, verbose_name=_("رقم الحساب"))
    iban = models.CharField(max_length=50, verbose_name=_("رقم الآيبان"))
    description = models.TextField(verbose_name=_("تعليمات الدفع"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    
    def __str__(self):
        return f"{self.hospital.name} - {self.payment_option.method_name}"
    
    class Meta:
        verbose_name = _("طريقة دفع المستشفى")
        verbose_name_plural = _("طرق دفع المستشفى")
        unique_together = ['hospital', 'payment_option']

# ------------Payment-------------


class Payment(models.Model):
    Type_choices = [
        ('cash', _('نقدي')),
        ('e_pay', _('دفع إلكتروني')),
    ]

    PaymentStatus_choices = [
        (0, _('قيد الانتظار')),
        (1, _('مكتمل')),
        (2, _('فشل')),
        (3, _('مسترد')),
    ]
    
    payment_method = models.ForeignKey(
        'HospitalPaymentMethod',
        on_delete=models.CASCADE,
        verbose_name=_("طريقة الدفع"),
        related_name='payments'
    )
    payment_status = models.IntegerField(  
        choices=PaymentStatus_choices,
        verbose_name=_("حالة الدفع"),
        default='pending'
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الدفع")
    )
    payment_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("المبلغ الفرعي")
    )
    payment_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("قيمة الخصم"),
        default=0
    )
    payment_totalamount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("المبلغ الإجمالي")
    )
    payment_currency = models.CharField(
        max_length=25,
        default='RYL',
        verbose_name=_("العملة")
    )
    payment_note = models.TextField(
        max_length=300,
        verbose_name=_("ملاحظات"),
        blank=True,
        null=True
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        verbose_name=_("الحجز"),
        related_name='payments'
    )
    payment_type = models.CharField(
        max_length=20,
        choices=Type_choices,
        verbose_name=_("نوع الدفع"),
        default='cash'
    )
    


    class Meta:
        verbose_name = _("فاتورة دفع")
        verbose_name_plural = _("فواتير الدفع")
        ordering = ['-payment_date']

    def get_status_display(self):
        """إرجاع النصوص الواضحة لحالة الدفع."""
        return dict(self.PaymentStatus_choices).get(self.payment_status, _("غير معروف"))

    def __str__(self):
        return f"فاتورة رقم {self.id} - {self.booking.patient.user.get_full_name} - {self.payment_totalamount} {self.payment_currency}"

    def save(self, *args, **kwargs):
        if self.payment_subtotal and self.payment_discount:
            self.payment_totalamount = self.payment_subtotal - self.payment_discount
        super().save(*args, **kwargs)


    def save(self, *args, **kwargs):
        # احسب المبلغ الكلي
        if self.payment_subtotal and self.payment_discount:
            self.payment_totalamount = self.payment_subtotal - self.payment_discount

        super().save(*args, **kwargs)

        # إذا تم الدفع بنجاح
        if self.payment_status == 1:
            booking = self.booking
            patient_user = booking.patient.user
            doctor_name = booking.doctor.user.get_full_name() if hasattr(booking.doctor, 'user') else str(booking.doctor)
            method_name = self.payment_method.payment_option.method_name

            # إنشاء رسالة الإشعار
            message = _(
                f"💳 *تم تأكيد الدفع*\n\n"
                f"عزيزي العميل،\n"
                f"تم استلام مبلغ *{self.payment_totalamount} {self.payment_currency}* بنجاح.\n"
                f"🧾 نوع الدفع: {self.get_payment_type_display()} عبر {method_name}\n"
                f"👨‍⚕️ الموعد مع الدكتور: *{doctor_name}*\n"
                f"📅 بتاريخ: {booking.booking_date}\n\n"
                f"شكرًا لاستخدامك خدمتنا، ونتطلع لخدمتك!"
            )

            # إرسال الإشعار
            Notifications.objects.create(
                sender=booking.hospital.admin_user if hasattr(booking.hospital, 'admin_user') else None,
                user=patient_user,
                message=message,
                notification_type='6'
            )

