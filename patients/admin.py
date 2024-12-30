from django.contrib import admin
from .models import Patients, Favourites
from doctors.models import Doctor

@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'birth_date', 'gender', 'phone_number', 'email', 'blood_group', 'join_date')
    list_filter = ('gender', 'join_date', 'blood_group') 
    search_fields = ('full_name', 'email', 'phone_number')

@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor') 
    search_fields = ('patient__full_name', 'doctor__name') 