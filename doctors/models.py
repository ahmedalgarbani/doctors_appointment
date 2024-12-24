from django.db import models
from hospitals.models import BaseModel
from django.urls import reverse

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
    STATUS_FAMEL = 0
    STATUS_MALE = 1

    STATUS_CHOICES = [
        (STATUS_MALE,'male'),
        (STATUS_FAMEL, 'famel'),
    ]
    full_name = models.CharField(max_length=255)
    birthday = models.DateField()
    phone_number = models.CharField(max_length=20)  
    hospitals = models.ManyToManyField('hospitals.Hospital', related_name='doctors',  
        )
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True,  
        blank=True)
    photo = models.ImageField(upload_to='doctor_images/', blank=True, null=True)
    gender =  models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_MALE,
    )
    email = models.EmailField(unique=True)  
    
    sub_title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200, unique=True)
    about = models.TextField()
    status = models.BooleanField(default=True)
    show_at_home = models.BooleanField(default=True)
    
    experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name="سنوات الخبرة"
    )

    def __str__(self):
        return self.full_name
  
    def get_absolute_url(self):
        return reverse('home:blog:post_detail', args=[self.slug])


# نموذج مواعيد الأطباء
class DoctorSchedules(models.Model):
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='schedules')
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, related_name='doctor_schedules', null=True,  
        blank=True)
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    available_slots = models.PositiveIntegerField(default=0)  

    def __str__(self):
        return f"{self.doctor} - {self.day}"

    class Meta:
        verbose_name = "جدول الطبيب"
        verbose_name_plural = "جداول الأطباء"
        ordering = [ 'day', 'start_time']

# Create your models here.



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

    def __str__(self):
        hospital_name = self.hospital.name if self.hospital else "No Hospital"
        return f"{self.doctor.full_name} - {hospital_name} - {self.amount}"

    class Meta:
        verbose_name = "جدول اسعار الطبيب"
        verbose_name_plural = "جداول اسعار الأطباء"
