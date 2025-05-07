from django.db import models
from hospitals.models import BaseModel, Hospital
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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
        verbose_name=_("صورة الإعلان")
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
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد المشاهدات")
    )
    clicks_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد النقرات")
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
