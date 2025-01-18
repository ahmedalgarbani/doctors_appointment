from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _



class CustomUser(AbstractUser):

    USER_TYPE_CHOICES = [
        ('admin', _('System Admin')),
        ('hospital_manager', _('Hospital Manager')),
        ('patient', _('Patient')),
    ]

    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, verbose_name=_("نوع المستخدم")
    )
    email = models.EmailField(unique=True, verbose_name=_("البريد الإلكتروني"))
    mobile_number = models.CharField(max_length=15, unique=True, verbose_name=_("رقم الهاتف"))
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True, verbose_name=_("الصورة الشخصية")
    )
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("المدينة"))
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("الولاية/المقاطعة"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile_number']

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"