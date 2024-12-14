from django.db import models
from hospitals.models import Hospital

# نموذج التخصصات
class Specialty(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='specialty/', blank=True, null=True)  
    show_at_home = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.name


# نموذج الأطباء
class Doctor(models.Model):
    full_name = models.CharField(max_length=255)
    birthday = models.DateField()
    phone_number = models.CharField(max_length=255)
    # hospital = models.ForeignKey('hospitals.Hospitals', on_delete=models.CASCADE,related_name='doctors')
    hospitals = models.ManyToManyField('hospitals.Hospitals', related_name='doctors')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='doctor_images/', blank=True, null=True)  
    email = models.EmailField()
    sub_title = models.CharField(max_length=255)
    about = models.TextField()
    status = models.BooleanField(default=True)
    show_at_home = models.BooleanField(default=True)
    
    def __str__(self):
        return self.full_name



# نموذج مواعيد الأطباء
class DoctorSchedules(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.name} - {self.day}"
