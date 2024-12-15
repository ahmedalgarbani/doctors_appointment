from django.contrib import admin
from .models import Patients, Favourites

@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'birth_date', 'gender', 'phone_number', 'email', 'join_date')
    list_filter = ('gender', 'join_date')
    search_fields = ('full_name', 'email', 'phone_number')

@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'doctor')
    search_fields = ('user__username', 'doctor__name')
