from django.db import models
<<<<<<< HEAD
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES=[
        ('admin','System Admin'),
        ('hospital_manager','Hospital Manager'),
        ('patients','patients'),]
    

    user_type=models.CharField(max_length=20,choices=USER_TYPE_CHOICES)
    mobile_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True)
    is_pregnant = models.BooleanField(default=False)
    pregnancy_term = models.PositiveSmallIntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_group = models.CharField(
        max_length=3,
        choices=[('A-', 'A-'), ('A+', 'A+'), ('B-', 'B-'), ('B+', 'B+'),
                 ('AB-', 'AB-'), ('AB+', 'AB+'), ('O-', 'O-'), ('O+', 'O+')],
        blank=True,
    )
    family_data = models.JSONField(default=dict, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return self.username
=======

# Create your models here.
>>>>>>> 98ca75c130f9cf6c22b7c0b3a95afd4a294c4972
