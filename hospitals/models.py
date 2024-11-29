from django.db import models

# Create your models here.

class Hospital(models.Model):
    name = models.CharField(max_length=100)
    hospital_manager_id = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def str(self):
        return self.name


class HospitalDetail(models.Model):
    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, related_name='details')
    description = models.TextField()
    doctor_count = models.IntegerField()
    specialty_count = models.IntegerField()

    def str(self):
        return f"Details for {self.hospital.name}"

class PhoneNumber(models.Model):
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='phone_numbers')
    specialty_id = models.IntegerField()

    def str(self):
        return f"{self.name} - {self.hospital.name}"

class HospitalDoctor(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='hospital_doctors')
    doctor_id = models.IntegerField()

    class Meta:
        unique_together = ('hospital', 'doctor_id')

    def str(self):
        return f"Doctor {self.doctor_id} at {self.hospital.name}"


