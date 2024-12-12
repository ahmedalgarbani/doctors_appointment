# في hospitals/models.py
from django.db import models

# نموذج المستشفيات
class Hospitals(models.Model):
    name = models.CharField(max_length=100)
    hospital_manager_id = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# تفاصيل المستشفى
class HospitalDetail(models.Model):
    hospital = models.OneToOneField(Hospitals, on_delete=models.CASCADE, related_name='details')
    description = models.TextField()
    doctor_count = models.IntegerField()
    specialty_count = models.IntegerField()

    def __str__(self):
        return f"Details for {self.hospital.name}"

# أرقام الهواتف
class PhoneNumber(models.Model):
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='phone_numbers')
    specialty = models.ForeignKey('doctors.Specialties', on_delete=models.SET_NULL, null=True, blank=True, related_name='phone_numbers')

    def __str__(self):
        return f"{self.name} - {self.hospital.name}"

# الأطباء في المستشفيات
class HospitalDoctor(models.Model):
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='hospital_doctors')
    doctor = models.ForeignKey('doctors.Doctors', on_delete=models.CASCADE, related_name='hospital_doctors', default=1)

    class Meta:
        unique_together = ('hospital', 'doctor')

    def __str__(self):
        return f"Doctor {self.doctor.name} at {self.hospital.name}"
