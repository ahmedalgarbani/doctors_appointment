from django.db import models
from hospitals.models import BaseModel
from django.conf import settings
from hospitals.models import BaseModel
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
        choices=[('Male', _('Male')), ('Female', _('Female'))],
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

class Favourites(BaseModel):
    patient = models.ForeignKey( 
        Patients,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name="المريض"
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='favourited_by',
        verbose_name="الطبيب"
    )

    class Meta:
        verbose_name = "المفضلات"
        verbose_name_plural = "المفضلات"
        constraints = [
            models.UniqueConstraint(fields=['patient', 'doctor'], name='unique_patient_doctor')
        ]

    def __str__(self):
        return f"{self.patient.user} - {self.doctor}"
