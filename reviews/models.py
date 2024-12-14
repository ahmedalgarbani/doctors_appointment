from django.db import models
from django.utils.translation import gettext_lazy as _
from hospitals.models import Hospital
from doctors.models import Doctor
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from hospitals.models import BaseModel

class Review(BaseModel):
    hospital = models.ForeignKey(
        Hospital, 
        on_delete=models.CASCADE,
        verbose_name=_("المستشفى"),
        related_name='reviews',
        null=True,  
        blank=True  
    )
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE,
        verbose_name=_("الدكتور"),
        related_name='reviews',
        null=True,  
        blank=True  
    )
    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("صاحب المراجعة"),
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name=_("التقييم"),
        choices=[(i, f"{i} نجوم" if i > 1 else "نجمة واحدة") for i in range(1, 6)],
        default=5,
        help_text=_("تقييم من 1 إلى 5 نجوم")
    )
    review = models.TextField(
        verbose_name=_("التعليق"),
        help_text=_("اكتب رأيك عن تجربتك في المستشفى")
    )
    status = models.BooleanField(
        verbose_name=_("نشط"),
        default=True,
        help_text=_("هل المراجعة مرئية للجميع؟")
    )
    has_reservation = models.BooleanField(
        verbose_name=_("لديه حجز"),
        default=False,
        help_text=_("هل قام المستخدم بالحجز في المستشفى؟")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("مراجعة")
        verbose_name_plural = _("المراجعات")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['hospital', 'user'],
                name='unique_hospital_user_review'
            )
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.hospital.name if self.hospital else 'غير محدد'} ({self.rating} نجوم)"

    def clean(self):
        super().clean()
        if not self.has_reservation:
            bookings = self.user.bookings.filter(hospital=self.hospital).exists()
            if bookings:
                self.has_reservation = True
            else:
                raise ValidationError(_("لا يمكنك كتابة مراجعة لمستشفى او طبيب لم تقم بالحجز عنده"))
