from django.db import models
from hospitals.models import BaseModel
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
import uuid

# نموذج التخصصات
class Specialty(BaseModel):
    name = models.CharField(max_length=255, verbose_name="الاسم")
    image = models.ImageField(upload_to='specialty/', blank=True, null=True, verbose_name="الصورة")
    show_at_home = models.BooleanField(default=True, verbose_name="عرض في الصفحة الرئيسية")
    status = models.BooleanField(default=True, verbose_name="الحالة")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "التخصص"
        verbose_name_plural = "التخصصات"


# نموذج الأطباء
class Doctor(BaseModel):
    STATUS_FEMALE = 0
    STATUS_MALE = 1

    STATUS_CHOICES = [
        (STATUS_MALE, 'ذكر'),
        (STATUS_FEMALE, 'أنثى'),
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
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="رابط الطبيب")
    about = RichTextField(verbose_name="عن الطبيب")
    status = models.BooleanField(default=True, verbose_name="الحالة")
    show_at_home = models.BooleanField(default=True, verbose_name="عرض في الصفحة الرئيسية")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug and self.full_name:
            base_slug = slugify(self.full_name)
            if not base_slug:  # If name doesn't generate valid slug
                base_slug = f'doctor-{self.pk or "new"}'
            
            # Handle slug duplication
            unique_slug = base_slug
            counter = 1
            while Doctor.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)
        
        # If we still don't have a slug after saving (in case of new doctor)
        if not self.slug:
            self.slug = f'doctor-{self.pk}'
            self.save(update_fields=['slug'])

    def get_absolute_url(self):
        return reverse('doctor:doctor_detail', args=[self.slug])

    class Meta:
        verbose_name = "الطبيب"
        verbose_name_plural = "الأطباء"


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
        verbose_name = "جدول ايام الطبيب"
        verbose_name_plural = "ايام الأطباء"


class DoctorShifts(models.Model):
    doctor_schedule = models.ForeignKey('DoctorSchedules', on_delete=models.CASCADE, related_name='shifts', verbose_name="جدول الطبيب")
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE, related_name='shifts', verbose_name="المستشفى")
    start_time = models.TimeField(verbose_name="وقت البداية")
    end_time = models.TimeField(verbose_name="وقت النهاية")
    available_slots = models.PositiveIntegerField(default=0, verbose_name="المواعيد المتاحة")
    booked_slots = models.PositiveIntegerField(default=0, verbose_name="المواعيد المحجوزة")

    def __str__(self):
        return f"{self.doctor_schedule} - {self.hospital.name} ({self.start_time} - {self.end_time})"

    @property
    def is_available(self):
        return self.available_slots > self.booked_slots

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError('وقت البداية يجب أن يكون قبل وقت النهاية')

        if self.available_slots < self.booked_slots:
            raise ValidationError('عدد المواعيد المتاحة لا يمكن أن يكون أقل من المواعيد المحجوزة')

        # التحقق من أن المستشفى مرتبط بالطبيب
        if not self.doctor_schedule.doctor.hospitals.filter(id=self.hospital.id).exists():
            raise ValidationError('هذا الطبيب لا يعمل في هذا المستشفى')

        # التحقق من عدم وجود تعارض في مواعيد الطبيب بين المستشفيات المختلفة
        doctor = self.doctor_schedule.doctor
        day = self.doctor_schedule.day

        # البحث عن جميع مواعيد الطبيب في نفس اليوم في جميع المستشفيات
        conflicting_schedules = DoctorSchedules.objects.filter(
            doctor=doctor,
            day=day
        ).exclude(hospital=self.hospital)

        # التحقق من كل جدول للتأكد من عدم وجود تداخل في الأوقات
        for schedule in conflicting_schedules:
            conflicting_shifts = DoctorShifts.objects.filter(
                doctor_schedule=schedule,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )

            if conflicting_shifts.exists():
                conflicting_shift = conflicting_shifts.first()
                hospital_name = conflicting_shift.hospital.name
                shift_time = f"{conflicting_shift.start_time.strftime('%H:%M')} - {conflicting_shift.end_time.strftime('%H:%M')}"
                raise ValidationError(
                    f'يوجد تعارض في المواعيد: الطبيب لديه موعد في مستشفى {hospital_name} '
                    f'في نفس اليوم من الساعة {shift_time}'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['doctor_schedule', 'hospital', 'start_time']
        verbose_name = "موعد"
        verbose_name_plural = "المواعيد"
        unique_together = ['doctor_schedule', 'hospital', 'start_time']


class DoctorPricing(models.Model):
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='pricing'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        related_name='doctor_prices',
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر"
    )
    transaction_number = models.CharField(
        max_length=256,
        default=uuid.uuid4,
        editable=False,
        verbose_name="رقم العملية"
    )

    def __str__(self):
        return f"{self.doctor.full_name} - {self.amount}"

    def save(self, *args, **kwargs):
        # If this is an update to an existing price
        if self.pk:
            old_price = DoctorPricing.objects.get(pk=self.pk)
            if old_price.amount != self.amount:
                # Create history record
                DoctorPricingHistory.objects.create(
                    doctor=self.doctor,
                    hospital=self.hospital,
                    amount=self.amount,
                    previous_amount=old_price.amount
                )
        else:
            # Create history record for new price
            DoctorPricingHistory.objects.create(
                doctor=self.doctor,
                hospital=self.hospital,
                amount=self.amount
            )

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "جدول اسعار الطبيب"
        verbose_name_plural = " اسعار الأطباء"


class DoctorPricingHistory(BaseModel):
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='pricing_history'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        related_name='doctor_price_history',
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر"
    )
    change_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التغيير")
    previous_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر السابق",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "سجل تغييرات أسعار الطبيب"
        verbose_name_plural = "سجلات تغييرات أسعار الأطباء"
        ordering = ['-change_date']

    def __str__(self):
        return f"{self.doctor.full_name} - {self.amount} ({self.change_date})"
