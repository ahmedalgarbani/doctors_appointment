from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from hospitals.models import Hospital, BaseModel

class StaffPermission(BaseModel):
    """نموذج صلاحيات الموظفين"""
    name = models.CharField(max_length=100, verbose_name=_("اسم الصلاحية"))
    codename = models.CharField(max_length=100, unique=True, verbose_name=_("الاسم الرمزي"))
    description = models.TextField(blank=True, null=True, verbose_name=_("وصف الصلاحية"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("صلاحية")
        verbose_name_plural = _("الصلاحيات")

class StaffRole(BaseModel):
    """نموذج أدوار الموظفين"""
    name = models.CharField(max_length=100, verbose_name=_("اسم الدور"))
    description = models.TextField(blank=True, null=True, verbose_name=_("وصف الدور"))
    permissions = models.ManyToManyField(
        StaffPermission,
        related_name='roles',
        verbose_name=_("الصلاحيات")
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='staff_roles',
        verbose_name=_("المستشفى")
    )
    is_default = models.BooleanField(default=False, verbose_name=_("دور افتراضي"))

    def __str__(self):
        return f"{self.name} - {self.hospital.name}"

    class Meta:
        verbose_name = _("دور وظيفي")
        verbose_name_plural = _("الأدوار الوظيفية")
        unique_together = ('name', 'hospital')

class HospitalStaff(BaseModel):
    """نموذج موظفي المستشفى"""
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('suspended', _('موقوف')),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hospital_staff',
        verbose_name=_("المستخدم")
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='staff',
        verbose_name=_("المستشفى")
    )
    role = models.ForeignKey(
        StaffRole,
        on_delete=models.SET_NULL,
        null=True,
        related_name='staff',
        verbose_name=_("الدور الوظيفي")
    )
    job_title = models.CharField(max_length=100, verbose_name=_("المسمى الوظيفي"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_("الحالة")
    )
    hire_date = models.DateField(verbose_name=_("تاريخ التعيين"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    is_first_login = models.BooleanField(default=True, verbose_name=_("أول تسجيل دخول"))

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.job_title} ({self.hospital.name})"

    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("الموظفين")
        unique_together = ('user', 'hospital')

# صلاحيات إضافية للموظف (خارج الدور الوظيفي)
class StaffAdditionalPermission(BaseModel):
    """صلاحيات إضافية للموظف خارج دوره الوظيفي"""
    staff = models.ForeignKey(
        HospitalStaff,
        on_delete=models.CASCADE,
        related_name='additional_permissions',
        verbose_name=_("الموظف")
    )
    permission = models.ForeignKey(
        StaffPermission,
        on_delete=models.CASCADE,
        related_name='staff_additional',
        verbose_name=_("الصلاحية")
    )
    granted = models.BooleanField(default=True, verbose_name=_("ممنوحة"))

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.permission.name}"

    class Meta:
        verbose_name = _("صلاحية إضافية")
        verbose_name_plural = _("الصلاحيات الإضافية")
        unique_together = ('staff', 'permission')
