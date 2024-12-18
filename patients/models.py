from django.db import models
from hospitals.models import BaseModel
from django.conf import settings
from hospitals.models import BaseModel

class Patients(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        verbose_name="المستخدم"
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name="الاسم الكامل"
    )
    birth_date = models.DateField(
        verbose_name="تاريخ الميلاد"
    )
    gender = models.CharField(
        max_length=10,
        choices=[('0', 'ذكر'), ('1', 'أنثى')],
        verbose_name="الجنس"
    )
    address = models.TextField(
        verbose_name="العنوان"
    )
    phone_number = models.CharField(
        max_length=15,
        verbose_name="رقم الهاتف"
    )
    email = models.EmailField(
        verbose_name="البريد الإلكتروني"
    )
    join_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الانضمام"
    )
    profile_picture = models.ImageField(
        upload_to='patient_pictures/',
        blank=True,
        null=True,
        verbose_name="صورة الملف الشخصي"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات"
    )

    def __str__(self):
        return self.full_name


class Favourites(BaseModel):
    patient = models.ForeignKey(  # Link directly to Patients
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
        return f"{self.patient.full_name} - {self.doctor}"
