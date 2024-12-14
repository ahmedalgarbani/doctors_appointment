from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patient')
    email = models.EmailField(unique=True, verbose_name="Email Address")
    mobile_number = models.CharField(
        max_length=15, unique=True, null=False, blank=False, verbose_name="Mobile Number"
    )
    profile_picture = models.ImageField(
        upload_to='uploads/profile_pictures/', null=True, blank=True, verbose_name="Profile Picture"
    )
    gender = models.CharField(
        max_length=10, 
        choices=[('male', 'Male'), ('female', 'Female')], 
        null=True, blank=True, verbose_name="Gender"
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPES,
        default='patient',
        verbose_name="User Type",
    )
    is_pregnant = models.BooleanField(default=False, verbose_name="Is Pregnant")
    pregnancy_term = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Pregnancy Term"
    )
    weight = models.FloatField(null=True, blank=True, verbose_name="Weight (kg)")
    height = models.FloatField(null=True, blank=True, verbose_name="Height (cm)")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Age")
    blood_group = models.CharField(
        max_length=5, 
        choices=[
            ('A+', 'A+'), ('A-', 'A-'), 
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'), 
            ('O+', 'O+'), ('O-', 'O-')
        ],
        null=True, blank=True, verbose_name="Blood Group"
    )
    family_data = models.JSONField(null=True, blank=True, verbose_name="Family Data")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="City")
    state = models.CharField(max_length=50, null=True, blank=True, verbose_name="State")

    # تعديل الحقول المتسببة في التعارض
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
