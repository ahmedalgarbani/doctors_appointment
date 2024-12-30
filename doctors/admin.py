from django.contrib import admin
from .models import Specialty, Doctor, DoctorSchedules, DoctorPricing

# تخصيص واجهة إدارة DoctorPricing
from .models import Doctor, Specialty, DoctorSchedules

# Register your models here.
from django.contrib import admin
from .models import DoctorPricing
from django.contrib import admin
from .models import DoctorShifts
# تخصيص واجهة إدارة Specialty
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_at_home', 'status') 
    list_filter = ('status', 'show_at_home') 
    search_fields = ('name',)
    ordering = ('name',)


# تخصيص واجهة إدارة Doctor
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'email', 'phone_number', 'status', 'show_at_home')
    list_filter = ('status', 'show_at_home', 'specialty')
    search_fields = ('full_name', 'email', 'phone_number')
    filter_horizontal = ('hospitals',)
    ordering = ('full_name',)
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('full_name', 'birthday', 'phone_number', 'email', 'photo')
        }),
        ('المستشفيات والتخصصات', {
            'fields': ('hospitals', 'specialty', 'sub_title', 'about')
        }),
        ('الإعدادات', {
            'fields': ('status', 'show_at_home')
        }),
    )




admin.site.register(DoctorSchedules)


@admin.register(DoctorShifts)
class DoctorShiftsAdmin(admin.ModelAdmin):
    list_display = ('doctor_schedule', 'start_time', 'end_time', 'available_slots', 'booked_slots')
    list_filter = ('doctor_schedule',)
    search_fields = ('doctor_schedule__id',)  # Adjust dules fields
    ordering = ('doctor_schedule', 'start_time')

    def get_queryset(self, request):
        # Customize queryset if needed (e.g., filter based on user)
        return super().get_queryset(request)

class DoctorPricingAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'hospital', 'amount') 
    search_fields = ('doctor__full_name', 'hospital__name')  
    list_filter = ('hospital',)
    ordering = ('doctor', 'hospital') 
    list_per_page = 20 

    fieldsets = (
        (None, {
            'fields': ('doctor', 'hospital', 'amount')
        }),
    )

admin.site.register(DoctorPricing, DoctorPricingAdmin)
