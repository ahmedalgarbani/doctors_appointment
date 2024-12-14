from django.db import models
from hospitals.models import BaseModel
from django.utils.translation import gettext_lazy as _

# Create your models here.


# ------------PaymentStatus-------------

class PaymentStatus(BaseModel):
    payment_status_name = models.CharField(
        max_length=50,
        verbose_name=_("اسم حالة الدفع")
    )
    status_code = models.IntegerField(
        verbose_name=_("رمز الحالة")
    )

    class Meta:
        verbose_name = _("حالة الدفع")
        verbose_name_plural = _("حالات الدفع")
        ordering = ['status_code']

    def __str__(self):
        return f"{self.payment_status_name} ({self.status_code})"


# ------------PaymentMethod-------------

class PaymentMethod(BaseModel):
    method_name = models.CharField(
        max_length=50,
        verbose_name=_("اسم طريقة الدفع")
    )
    logo = models.ImageField(
        upload_to='payment_methods/',
        verbose_name=_("الشعار"),
        null=True,
        blank=True
    )
    activate_state = models.BooleanField(
        default=True,
        verbose_name=_("مفعّل")
    )
    country = models.CharField(
        max_length=50,
        verbose_name=_("الدولة")
    )
    currency = models.CharField(
      default='RYL',
        verbose_name=_("العملة"),
        related_name='payment_methods'
    )
    transfer_number = models.CharField(
        max_length=66,
        verbose_name=_("رقم التحويل"),
        blank=True,
        null=True
    )
    description = models.TextField(
        max_length=300,
        verbose_name=_("الوصف"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("طريقة الدفع")
        verbose_name_plural = _("طرق الدفع")
        ordering = ['-activate_state', 'method_name']

    def __str__(self):
        status = _("مفعّل") if self.activate_state else _("معطّل")
        return f"{self.method_name} - {self.currency.currency_symbol} ({status})"


# ------------Payment-------------

class Payment(BaseModel):
    Type_choices = [
        ('cash', _('نقدي')),
        ('e_pay', _('دفع إلكتروني')),
    ]

    payment_method = models.ForeignKey(
        'payments.PaymentMethod',
        on_delete=models.CASCADE,
        verbose_name=_("طريقة الدفع"),
        related_name='payments'
    )
    payment_status = models.ForeignKey(
        'payments.PaymentStatus',
        on_delete=models.CASCADE,
        verbose_name=_("حالة الدفع"),
        related_name='payments'
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
      default='RYL',
        verbose_name=_("العملة"),
        related_name='payment_methods'
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

    def __str__(self):
        return f"فاتورة رقم {self.id} - {self.booking.guest.name if self.booking.guest else 'غير محدد'} - {self.payment_totalamount} {self.payment_currency.currency_symbol}"

    def save(self, *args, **kwargs):
        if self.payment_subtotal and self.payment_discount:
            self.payment_totalamount = self.payment_subtotal - self.payment_discount
        super().save(*args, **kwargs)