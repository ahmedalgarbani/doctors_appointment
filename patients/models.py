from django.db import models
from hospitals import BaseModel
class Patients(BaseModel):
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='patients')
    full_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10) 
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    join_date = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='patient_pictures/', blank=True, null=True)  
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
    
class Favourites(BaseModel):
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='favourites')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='favourites')

