from django.db import models

# Create your models here.
class Bookings(models.Model):
    patient = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='patient_bookings')
    doctor = models.ForeignKey('doctors.Doctors', on_delete=models.CASCADE)
    hospital = models.ForeignKey('hospitals.Hospitals', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=50)
