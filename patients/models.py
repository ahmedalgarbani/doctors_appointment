from datetime import date
from django.db import models
from hospitals.models import BaseModel
from django.conf import settings
from users.models import CustomUser
from django.utils.translation import gettext_lazy as _

class Patients(BaseModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='patient',
        verbose_name=_("حساب المستخدم"),
        limit_choices_to={'user_type': 'patient'},  
    )
    birth_date = models.DateField(verbose_name=_("تاريخ الميلاد"))
    gender = models.CharField(
        max_length=10,
        choices=[('Male', _('ذكر')), ('Female', _('أنثى'))],
        verbose_name=_("الجنس"),
    )
    weight = models.FloatField(null=True, blank=True, verbose_name=_("الوزن (كجم)"))
    height = models.FloatField(null=True, blank=True, verbose_name=_("الطول (سم)"))
    age = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("العمر"))
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        null=True,
        blank=True,
        verbose_name=_("فصيلة الدم"),
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    def __str__(self):
        return f"{self.user.username} ({self.user.email})"

    class Meta:
        verbose_name = _("المرضى")
        verbose_name_plural = _("المرضى")

    def calculate_age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def save(self, *args, **kwargs):
        if self.birth_date and not self.age:
            self.age = self.calculate_age()
        super().save(*args, **kwargs)


class Favourites(BaseModel):
    patient = models.ForeignKey( 
        Patients,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name=_("المريض")
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='favourited_by',
        verbose_name=_("الطبيب")
    )

    class Meta:
        verbose_name = _("المفضلة")
        verbose_name_plural = _("المفضلات")
        constraints = [
            models.UniqueConstraint(fields=['patient', 'doctor'], name='unique_patient_doctor')
        ]

    def __str__(self):
        return f"{self.patient.user} - {self.doctor}"
