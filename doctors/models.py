from django.db import models
from hospitals.models import BaseModel
from django.utils.text import slugify
from django.db.models import Max

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
            base_slug = slugify(self.full_name)  # توليد السلا slug باستخدام الاسم الكامل
            if not base_slug:
                base_slug = 'default-slug'  # إضافة قيمة افتراضية إذا كانت القيمة فارغة

            # التحقق من وجود سجل مشابه
            existing_slugs = Doctor.objects.filter(slug__startswith=base_slug)
            if existing_slugs.exists():
                max_slug = existing_slugs.aggregate(max_count=Max('slug'))
                # استخراج الرقم الأكبر الموجود
                max_slug_num = 0
                for doctor in existing_slugs:
                    try:
                        num_part = doctor.slug.split('-')[-1]
                        max_slug_num = max(max_slug_num, int(num_part))
                    except ValueError:
                        continue
                    
                self.slug = f"{base_slug}-{str(max_slug_num + 1)}"  # إضافة الرقم الجديد
            else:
                self.slug = base_slug  # إذا لم يكن هناك تكرار

        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('home:blog:post_detail', args=[self.slug])

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
            # توليد السلا slug باستخدام الاسم الكامل
            base_slug = slugify(self.full_name)
            # التأكد من عدم وجود تكرار في السلا slug
            existing_slugs = Doctor.objects.filter(slug__startswith=base_slug).aggregate(max_count=Max('slug'))
            count = existing_slugs.get('max_count', 0)
            if count:
                self.slug = f"{base_slug}-{str(count + 1)}"  # تحويل count إلى str
            else:
                self.slug = base_slug

        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('home:blog:post_detail', args=[self.slug])

        

class DoctorSchedules(models.Model):
    DAY_CHOICES = [
        (0, 'Saturday'),
        (1, 'Sunday'),
        (2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
    ]
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='schedules')
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, related_name='doctor_schedules', null=True, blank=True)
    day = models.CharField(max_length=20, choices=DAY_CHOICES) 

    def __str__(self):
        return f"{self.doctor} - {self.day}"

    class Meta:
        ordering = ['day', 'doctor']


class DoctorShifts(models.Model):
    doctor_schedule = models.ForeignKey('DoctorSchedules', on_delete=models.CASCADE, related_name='shifts')
    start_time = models.TimeField()      
    end_time = models.TimeField()        
    available_slots = models.PositiveIntegerField(default=0)
    booked_slots = models.PositiveIntegerField(default=0)    

    def __str__(self):
        return f"Shift from {self.start_time} to {self.end_time}"




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
