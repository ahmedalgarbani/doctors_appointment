from django.db import models
from django.utils.translation import gettext_lazy as _
from hospitals.models import BaseModel
from django.conf import settings

class Notifications(BaseModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name=_("المرسل")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name=_("المستلم")
    )
    message = models.TextField(verbose_name=_("الرسالة"))
    send_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("وقت الإرسال")
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('0', _("غير مقروء")),
            ('1', _("مقروء")),
        ],
        default='0',
        verbose_name=_("الحالة")
    )
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('0', _("معلومة")),
            ('1', _("تحذير")),
            ('2', _("نجاح")),
            ('3', _("خطأ")),
        ],
        verbose_name=_("نوع الإشعار")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )

    class Meta:
        verbose_name = _("إشعار")
        verbose_name_plural = _("الإشعارات")
        ordering = ['-send_time']

    def __str__(self):
        return f"Notification from {self.sender} to {self.user} - {self.notification_type}"

# Create your models here.
