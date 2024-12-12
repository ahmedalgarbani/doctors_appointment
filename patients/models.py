from django.db import models

class Patients(models.Model):
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='patients')
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10) 
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    health_status = models.TextField(blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='patient_pictures/', blank=True, null=True)  
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
