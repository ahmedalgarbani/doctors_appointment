from django.db import models
from hospitals.models import Hospital


class Specialties(models.Model):
    specialty_name = models.CharField(max_length=255)
    

    def __str__(self):
        return self.specialty_name


class Doctors(models.Model):
    name = models.CharField(max_length=255)
    hospitel_id = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE)
    specialty_id = models.ForeignKey(Specialties, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class DoctorRates(models.Model):
    doctor_id = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    hospitel_id = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.doctor_id.name} - {self.rate}" 


class DoctorSchedules(models.Model):
    doctor_id = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    hospitel_id = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor_id.name} - {self.day}" 
