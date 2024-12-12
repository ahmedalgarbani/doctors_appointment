from django.db import models
from hospitals.models import Hospitals

# نموذج التخصصات
class Specialties(models.Model):
    specialty_name = models.CharField(max_length=255)

    def __str__(self):
        return self.specialty_name


# نموذج الأطباء
class Doctors(models.Model):
    name = models.CharField(max_length=255)
    hospital = models.ForeignKey('hospitals.Hospitals', on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialties, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='doctor_images/', blank=True, null=True)  

    def __str__(self):
        return self.name


# نموذج تقييمات الأطباء
class DoctorRates(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.doctor.name} - {self.rate}"


# نموذج مواعيد الأطباء
class DoctorSchedules(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.name} - {self.day}"
