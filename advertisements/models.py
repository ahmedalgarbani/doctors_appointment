from django.db import models
from hospitals.models import BaseModel, Hospital
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import FileExtensionValidator

def advertisement_image_path(instance, filename):
    # Use the hospital ID to create a unique path for advertisement images
    return f'advertisements/hospital_{instance.hospital.id}/{filename}'

class Advertisement(BaseModel):
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('scheduled', _('مجدول')),
        ('expired', _('منتهي')),
    ]

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='advertisements',
        verbose_name=_("المستشفى")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("عنوان الإعلان")
    )
    description = models.TextField(
        verbose_name=_("وصف الإعلان")
    )
    image = models.ImageField(
        upload_to=advertisement_image_path,
        blank=True,
        null=True,
        verbose_name=_("صورة الإعلان الرئيسية")
    )
    image2 = models.ImageField(
        upload_to=advertisement_image_path,
        blank=True,
        null=True,
        verbose_name=_("صورة إضافية 1")
    )
    image3 = models.ImageField(
        upload_to=advertisement_image_path,
        blank=True,
        null=True,
        verbose_name=_("صورة إضافية 2")
    )
    image4 = models.ImageField(
        upload_to=advertisement_image_path,
        blank=True,
        null=True,
        verbose_name=_("صورة إضافية 3")
    )
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_("تاريخ البدء")
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("تاريخ الانتهاء"),
        help_text=_("اتركه فارغاً إذا كان الإعلان غير محدد المدة")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_("الحالة")
    )

    class Meta:
        verbose_name = _("إعلان")
        verbose_name_plural = _("الإعلانات")
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        today = timezone.now().date()
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < today:
            return False
        return True

    def update_status(self):
        """Update the status based on dates"""
        today = timezone.now().date()

        if self.status == 'active' and self.end_date and self.end_date < today:
            self.status = 'expired'
            self.save(update_fields=['status'])
        elif self.status == 'scheduled' and self.start_date <= today:
            self.status = 'active'
            self.save(update_fields=['status'])

        return self.status


def advertisement_additional_image_path(instance, filename):
    # Use the advertisement ID to create a unique path for additional images
    return f'advertisements/hospital_{instance.advertisement.hospital.id}/ad_{instance.advertisement.id}/{filename}'


class AdvertisementImage(BaseModel):
    """Model for additional advertisement images"""
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='additional_images',
        verbose_name=_("الإعلان")
    )
    image = models.ImageField(
        upload_to=advertisement_additional_image_path,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        verbose_name=_("الصورة")
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("الترتيب")
    )

    class Meta:
        verbose_name = _("صورة إعلان")
        verbose_name_plural = _("صور الإعلانات")
        ordering = ['advertisement', 'order']

    def __str__(self):
        return f"{self.advertisement.title} - صورة {self.order + 1}"
