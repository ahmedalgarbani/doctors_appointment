from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from users.models import CustomUser
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التعديل")
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الحذف")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_created",
        verbose_name=_("المنشى"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_updated",
        verbose_name=_("المعدل"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        
    )
  

    class Meta:
        abstract = True

class City(models.Model):
    name = models.CharField(max_length=100, unique=True ,)
    slug = models.SlugField(unique=True)
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.name
  


# نموذج المستشفيات
class Hospital(BaseModel):
    name = models.CharField(max_length=100)
    hospital_manager = models.OneToOneField(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    location = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("المدينة"))  
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home:hospitals:hospital_detail', args=[self.slug])


# تفاصيل المستشفى
class HospitalDetail(BaseModel):
    hospital = models.OneToOneField('hospitals.Hospital', on_delete=models.CASCADE, related_name='details')
    description = models.TextField()
    specialty = models.ForeignKey('doctors.Specialty', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='hospital_images/', blank=True, null=True)
    sub_title = models.CharField(max_length=255)
    about = models.TextField()
    status = models.BooleanField(default=True)
    show_at_home = models.BooleanField(default=True)

    def __str__(self):
        return f"Details for {self.hospital.description}"


# أرقام الهواتف
class PhoneNumber(BaseModel):
    number = models.CharField(max_length=14)  
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='phone_numbers')
    phone_type = models.CharField(  
        max_length=50,
        choices=[
            ('landline', _("هاتف أرضي")),
            ('mobile', _("هاتف محمول"))
        ],
        default='mobile',
        verbose_name=_("نوع الهاتف")
    )

    def __str__(self):
        return f"{self.number} ({self.phone_type}) - {self.hospital.name}"


# طلبات فتح حساب المستشفى
class HospitalAccountRequest(BaseModel):
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('approved', _('تمت الموافقة')),
        ('rejected', _('مرفوض')),
    ]

    hospital_name = models.CharField(
        max_length=100,
        verbose_name=_("اسم المستشفى")
    )
    manager_full_name = models.CharField(
        max_length=255,
        verbose_name=_("اسم مدير المستشفى")
    )
    manager_email = models.EmailField(
        verbose_name=_("البريد الإلكتروني للمدير")
    )
    manager_phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم هاتف المدير")
    )
    manager_password = models.CharField(
        max_length=128,
        verbose_name=_("كلمة المرور"),
        help_text=_("كلمة المرور التي سيتم استخدامها لحساب مدير المستشفى")
    )
    hospital_location = models.CharField(
        max_length=255,
        verbose_name=_("موقع المستشفى")
    )
    commercial_record = models.FileField(
        upload_to='hospital_documents/',
        verbose_name=_("السجل التجاري"),
        help_text=_("يرجى رفع نسخة من السجل التجاري للمستشفى")
    )
    medical_license = models.FileField(
        upload_to='hospital_documents/',
        verbose_name=_("الترخيص الطبي"),
        help_text=_("يرجى رفع نسخة من الترخيص الطبي للمستشفى")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("حالة الطلب")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("ملاحظات"),
        help_text=_("ملاحظات إضافية حول الطلب")
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_hospital_requests',
        verbose_name=_("تمت المراجعة بواسطة")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المراجعة")
    )

    class Meta:
        verbose_name = _("طلب فتح حساب مستشفى")
        verbose_name_plural = _("طلبات فتح حساب مستشفى")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.hospital_name} - {self.get_status_display()}"

    def approve_request(self, reviewed_by):
        from django.utils import timezone
        self.status = 'approved'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.save()

    def reject_request(self, reviewed_by, notes=None):
        from django.utils import timezone
        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()
