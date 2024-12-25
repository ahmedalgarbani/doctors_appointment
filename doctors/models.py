from django.db import models
from hospitals.models import BaseModel
from django.urls import reverse
from django.utils.text import slugify

# نموذج التخصصات
class Specialty(BaseModel):
    name = models.CharField(max_length=255, verbose_name="اسم التخصص")
    image = models.ImageField(upload_to='specialty/', blank=True, null=True, verbose_name="صورة التخصص")
    show_at_home = models.BooleanField(default=True, verbose_name="عرض في الصفحة الرئيسية")
    status = models.BooleanField(default=True, verbose_name="الحالة")

    def __str__(self):
        return self.name


# نموذج الأطباء
class Doctor(BaseModel):
    STATUS_FAMEL = 0
    STATUS_MALE = 1

    STATUS_CHOICES = [
        (STATUS_MALE, 'ذكر'),
        (STATUS_FAMEL, 'أنثى'),
    ]

    full_name = models.CharField(max_length=255, verbose_name="الاسم الكامل")
    birthday = models.DateField(verbose_name="تاريخ الميلاد")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    hospitals = models.ManyToManyField('hospitals.Hospital', related_name='doctors', blank=True, verbose_name="المستشفيات")
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="التخصص")
    photo = models.ImageField(upload_to='doctor_images/', blank=True, null=True, verbose_name="الصورة الشخصية")
    gender = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_MALE, verbose_name="الجنس")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    experience = models.IntegerField(default=0, verbose_name="الخبرة")
    sub_title = models.CharField(max_length=255, verbose_name="العنوان الفرعي")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="رابط الطبيب")
    about = models.TextField(verbose_name="نبذة عن الطبيب")
    status = models.BooleanField(default=True, verbose_name="الحالة")
    show_at_home = models.BooleanField(default=True, verbose_name="عرض في الصفحة الرئيسية")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="سنوات الخبرة")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
        if not self.slug:
            self.slug = 'default-slug'  
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('home:blog:post_detail', args=[self.slug])


# نموذج مواعيد الأطباء
class DoctorSchedules(models.Model):
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='schedules', verbose_name="الطبيب")
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, related_name='doctor_schedules', null=True, blank=True, verbose_name="المستشفى")
    day = models.CharField(max_length=20, verbose_name="اليوم")
    start_time = models.TimeField(verbose_name="وقت البدء")
    end_time = models.TimeField(verbose_name="وقت الانتهاء")
    available_slots = models.PositiveIntegerField(default=0, verbose_name="عدد المواعيد المتاحة")

    def __str__(self):
        return f"{self.doctor} - {self.day}"

    class Meta:
        verbose_name = "جدول الطبيب"
        verbose_name_plural = "جداول الأطباء"
        ordering = ['day', 'start_time']


# نموذج أسعار الأطباء
class DoctorPricing(models.Model):
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='pricing', verbose_name="الطبيب")
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, related_name='doctor_prices', null=True, blank=True, verbose_name="المستشفى")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")

    def __str__(self):
        hospital_name = self.hospital.name if self.hospital else "لا يوجد مستشفى"
        return f"{self.doctor.full_name} - {hospital_name} - {self.amount}"

    class Meta:
        verbose_name = "جدول اسعار الطبيب"
        verbose_name_plural = "جداول اسعار الأطباء"
