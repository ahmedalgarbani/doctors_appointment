from django.contrib import admin
from .models import Hospital, HospitalDetail, PhoneNumber


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'hospital_manager_id', 'created_at')
    search_fields = ('name', 'location')
    ordering = ('-created_at',)


@admin.register(HospitalDetail)
class HospitalDetailAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'specialty', 'status', 'show_at_home')
    search_fields = ('hospital__name', 'specialty__name')
    list_filter = ('status', 'show_at_home')


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'phone_type', 'hospital')
    search_fields = ('number', 'hospital__name')
    list_filter = ('phone_type',)