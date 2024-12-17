from django.db import models
<<<<<<< HEAD
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class RegistrationRequests(models.Model):
    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2
    STATUS_CANCELLED = 3

    STATUS_CHOICES = [
        (STATUS_PENDING, _('قيد الانتظار')),
        (STATUS_APPROVED, _('تمت الموافقة')),
        (STATUS_REJECTED, _('مرفوض')),
        (STATUS_CANCELLED, _('ملغي')),
    ]

    application_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_("حالة الطلب"),
        help_text=_('الحالة الحالية لطلب التسجيل')
    )
    notes = models.TextField(blank=True, null=True)
    full_name = models.CharField(
        max_length=100,
        verbose_name=_('اسم المالك'),
        help_text=_('الاسم الكامل لمالك المستشفى')
    )
    hotel_name = models.CharField(
        max_length=100,
        verbose_name=_('اسم المستشفى'),
        help_text=_('اسم المستشفى كما سيظهر في النظام')
    )
    email = models.EmailField()
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("رقم الهاتف يجب أن يكون بالصيغة: '+999999999'. يسمح بإدخال من 9 إلى 15 رقم.")
    )
    phone = models.CharField(
        max_length=20,
        validators=[phone_regex],
        verbose_name=_('رقم الهاتف'),
        help_text=_('رقم الهاتف الرسمي للمالك')
    ) 
    
    business_license_number = models.CharField(
        max_length=50,
        verbose_name=_('رقم الرخصة الطبية'),
        null=True,
        blank=True,
        help_text=_('رقم الرخصة للمستشفى')
    )   
    
    document_path = models.FileField(
        upload_to='hospital_documents/%Y/%m/%d/',
        verbose_name=_('مستندات المستشفى'),
        help_text=_('المستندات الرسمية للمستشفى (رخصة العمل، السجل التجاري، إلخ)')
    )
    
    verify_number = models.CharField(
        max_length=50,
        verbose_name=_('رقم التحقق'),
        unique=True,
        help_text=_('رقم التحقق الخاص بطلب التسجيل')
    )

    attached_documents = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(blank=True, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("ملاحظات المسؤول"),
        help_text=_('ملاحظات المسؤول حول الطلب')
    )
    password = models.CharField(
        max_length=255,
        verbose_name=_("كلمة السر"),
        help_text=_('كلمة السر المؤقتة للحساب')
    )
    verify_code = models.CharField(max_length=6)  
    block_end = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('طلب حساب مستشفى')
        verbose_name_plural = _('طلبات حسابات المستشفيات')
        ordering = ['-application_date'] 

    def __str__(self):
        return f"{self.hotel_name} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        if self.status == self.STATUS_APPROVED and not self.admin_notes:
            raise ValidationError({
                'admin_notes': _('يجب إضافة ملاحظات عند الموافقة على الطلب')
            })
        
        if self.status == self.STATUS_REJECTED and not self.admin_notes:
            raise ValidationError({
                'admin_notes': _('يجب إضافة سبب الرفض')
            })
=======

# Create your models here.
>>>>>>> 98ca75c130f9cf6c22b7c0b3a95afd4a294c4972
