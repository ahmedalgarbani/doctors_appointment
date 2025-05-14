from django.contrib import admin
from .models import Patients, Favourites


@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_filter = ('gender',)  # Filters on the right panel
    search_fields = ('user__email', 'user__mobile_number')  # Searchable fields
    ordering = ('-gender',)  # Default ordering
    readonly_fields = ('gender',)  # Fields that can't be edited


    def get_queryset(self, request):
        # Customize the queryset if needed
        return super().get_queryset(request)


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor')  # Columns to display
    search_fields = ('patient__full_name', 'doctor__full_name')  # Searchable fields (related fields)
    list_filter = ('patient', 'doctor')  # Filters on the right panel
    ordering = ('patient',)  # Default ordering
    autocomplete_fields = ('patient', 'doctor')  # Autocomplete for related fields

    def get_queryset(self, request):
        # Customize the queryset if needed
        return super().get_queryset(request)
