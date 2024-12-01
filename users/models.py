from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
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

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username
