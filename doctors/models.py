from django.db import models
from hospitals.models import BaseModel
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField

# نموذج التخصصات
class Specialty(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='specialty/', blank=True, null=True)
    show_at_home = models.BooleanField(default=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# نموذج الأطباء
class Doctor(BaseModel):
    STATUS_FEMALE = 0
    STATUS_MALE = 1

    STATUS_CHOICES = [
        (STATUS_MALE, 'Male'),
        (STATUS_FEMALE, 'Female'),
    ]

    full_name = models.CharField(max_length=255, verbose_name="الاسم الكامل")
    birthday = models.DateField(verbose_name="تاريخ الميلاد")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    hospitals = models.ManyToManyField('hospitals.Hospital', related_name='doctors', blank=True, verbose_name="المستشفيات")
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="التخصص")
    photo = models.ImageField(upload_to='doctor_images/', blank=True, null=True, verbose_name="الصورة الشخصية")
    gender = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_MALE, verbose_name="الجنس")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="سنوات الخبرة")
    sub_title = models.CharField(max_length=255, verbose_name="العنوان الفرعي")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="رابط الطبيب")
    about = RichTextField()
    status = models.BooleanField(default=True, verbose_name="الحالة")
    show_at_home = models.BooleanField(default=True, verbose_name="عرض في الصفحة الرئيسية")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
        
        # Handle slug duplication
        from django.db.models import Q
        unique_slug = self.slug
        counter = 1
        while Doctor.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f"{self.slug}-{counter}"
            counter += 1
        self.slug = unique_slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('home:blog:post_detail', args=[self.slug])


# نموذج مواعيد الأطباء
class DoctorSchedules(models.Model):
    DAY_CHOICES = [
        (0, 'السبت'),
        (1, 'الأحد'),
        (2, 'الإثنين'),
        (3, 'الثلاثاء'),
        (4, 'الأربعاء'),
        (5, 'الخميس'),
        (6, 'الجمعة'),
    ]
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='schedules', verbose_name="الطبيب")
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, related_name='doctor_schedules', null=True, blank=True, verbose_name="المستشفى")
    day = models.IntegerField(choices=DAY_CHOICES, verbose_name="اليوم")

    def __str__(self):
        return f"{self.doctor} - {self.get_day_display()}"

    class Meta:
        ordering = ['day', 'doctor']
        verbose_name = "جدول الطبيب"
        verbose_name_plural = "جداول الأطباء"
        unique_together = ['doctor', 'day']  # لا يمكن للطبيب أن يكون له أكثر من جدول في نفس اليوم


class DoctorShifts(models.Model):
    doctor_schedule = models.ForeignKey('DoctorSchedules', on_delete=models.CASCADE, related_name='shifts', verbose_name="جدول الطبيب")
    start_time = models.TimeField(verbose_name="وقت البداية")
    end_time = models.TimeField(verbose_name="وقت النهاية")
    available_slots = models.PositiveIntegerField(default=0, verbose_name="المواعيد المتاحة")
    booked_slots = models.PositiveIntegerField(default=0, verbose_name="المواعيد المحجوزة")

    def __str__(self):
        return f"{self.doctor_schedule} ({self.start_time} - {self.end_time})"
    
    @property
    def is_available(self):
        return self.available_slots > self.booked_slots
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError('وقت البداية يجب أن يكون قبل وقت النهاية')
        
        if self.available_slots < self.booked_slots:
            raise ValidationError('عدد المواعيد المتاحة لا يمكن أن يكون أقل من المواعيد المحجوزة')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['doctor_schedule', 'start_time']
        verbose_name = "موعد"
        verbose_name_plural = "المواعيد"
        unique_together = ['doctor_schedule', 'start_time']  # لا يمكن أن يكون هناك موعدان بنفس وقت البداية لنفس الجدول


class DoctorPricing(models.Model):
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='pricing')
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, related_name='doctor_prices', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")

    def __str__(self):
        hospital_name = self.hospital.name if self.hospital else "No Hospital"
        return f"{self.doctor.full_name} - {hospital_name} - {self.amount}"

    class Meta:
        verbose_name = "جدول اسعار الطبيب"
        verbose_name_plural = "جداول اسعار الأطباء"
