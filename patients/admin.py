from django.contrib import admin
from .models import Patients, Favourites

# Admin interface for Patients model
@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date', 'gender', 'phone_number', 'email', 'join_date')
    list_filter = ('gender', 'join_date')
    search_fields = ('full_name', 'phone_number', 'email')
    ordering = ('-join_date',)
    readonly_fields = ('join_date',)

    def get_queryset(self, request):
        # Optionally, modify the queryset (e.g., filter based on user)
        return super().get_queryset(request)

# Admin interface for Favourites model
@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor')
    search_fields = ('patient__full_name', 'doctor__full_name')
    list_filter = ('patient', 'doctor')
    ordering = ('patient',)

    def get_queryset(self, request):
        # Optionally, customize the queryset to filter based on user
        return super().get_queryset(request)
