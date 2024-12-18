from django.contrib import admin
from .models import Doctor, Specialty, DoctorSchedules

admin.site.register(Doctor)
admin.site.register(Specialty)
admin.site.register(DoctorSchedules)

# Register your models here.
from django.contrib import admin
from .models import DoctorPricing

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
