from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'hospital', 'appointment_date', 'appointment_time', 'status', 'is_online')
    
    list_filter = ('status', 'is_online', 'appointment_date', 'doctor', 'hospital')
    
    search_fields = ('patient', 'doctor__name', 'hospital__name', 'notes')
    
    ordering = ['-appointment_date', '-appointment_time']

admin.site.register(Booking, BookingAdmin)
