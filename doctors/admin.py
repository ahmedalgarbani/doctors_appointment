from django.contrib import admin
from .models import Doctor, Specialty, DoctorSchedules

admin.site.register(Doctor)
admin.site.register(Specialty)
admin.site.register(DoctorSchedules)

# Register your models here.
from django.contrib import admin
from .models import DoctorPricing
from django.contrib import admin
from .models import DoctorShifts

@admin.register(DoctorShifts)
class DoctorShiftsAdmin(admin.ModelAdmin):
    list_display = ('doctor_schedule', 'start_time', 'end_time', 'available_slots', 'booked_slots')
    list_filter = ('doctor_schedule',)
    search_fields = ('doctor_schedule__id',)  # Adjust as per the DoctorSchedules fields
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
