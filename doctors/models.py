from django.db import models
from hospitals.models import BaseModel

# نموذج التخصصات
class Specialty(BaseModel):
    name = models.CharField(max_length=255, verbose_name="اسم التخصص")
    image = models.ImageField(upload_to='specialty/', blank=True, null=True, verbose_name="صورة التخصص")
    show_at_home = models.BooleanField(default=True, verbose_name="عرض في الصفحة الرئيسية")
    status = models.BooleanField(default=True, verbose_name="الحالة")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "تخصص"
        verbose_name_plural = "التخصصات"
        ordering = ['name']


# نموذج الأطباء
class Doctor(BaseModel):
    full_name = models.CharField(max_length=255, verbose_name="الاسم الكامل")
    birthday = models.DateField(verbose_name="تاريخ الميلاد")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    hospitals = models.ManyToManyField(
        'hospitals.Hospital', 
        related_name='doctors', 
        blank=True, 
        verbose_name="المستشفيات"
    )
    specialty = models.ForeignKey(
        Specialty, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="التخصص"
    )
    photo = models.ImageField(upload_to='doctor_images/', blank=True, null=True, verbose_name="الصورة الشخصية")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    sub_title = models.CharField(max_length=255, verbose_name="العنوان الفرعي")
    about = models.TextField(verbose_name="نبذة عن الطبيب")
    status = models.BooleanField(default=True, verbose_name="الحالة")
    show_at_home = models.BooleanField(default=True, verbose_name="عرض في الصفحة الرئيسية")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "طبيب"
        verbose_name_plural = "الأطباء"
        ordering = ['full_name']


# نموذج مواعيد الأطباء
class DoctorSchedules(models.Model):
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        related_name='schedules', 
        verbose_name="الطبيب"
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital', 
        on_delete=models.SET_NULL, 
        related_name='doctor_schedules', 
        null=True, 
        blank=True, 
        verbose_name="المستشفى"
    )
    day = models.CharField(max_length=20, verbose_name="اليوم")
    start_time = models.TimeField(verbose_name="وقت البدء")
    end_time = models.TimeField(verbose_name="وقت الانتهاء")
    available_slots = models.PositiveIntegerField(
        default=0, 
        verbose_name="عدد المواعيد المتاحة", 
        help_text="عدد المواعيد المتاحة لهذا اليوم."
    )

    def __str__(self):
        return f"{self.doctor.full_name} - {self.day}"

    class Meta:
        verbose_name = "جدول الطبيب"
        verbose_name_plural = "جداول الأطباء"
        ordering = ['day', 'start_time']


