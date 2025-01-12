from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'System Admin'),
        ('hospital_manager', 'Hospital Manager'),
        ('patients', 'Patients'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)  # Ensure email is unique
    mobile_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True)
    is_pregnant = models.BooleanField(default=False)
    pregnancy_term = models.PositiveSmallIntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        null=True, blank=True, verbose_name="Blood Group"
    )
    family_data = models.JSONField(null=True, blank=True, verbose_name="Family Data")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="City")
    state = models.CharField(max_length=50, null=True, blank=True, verbose_name="State")

    # Override default groups and permissions to prevent conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Required fields for custom user authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile_number']

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
