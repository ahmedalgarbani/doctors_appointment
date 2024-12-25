from django.contrib import admin
from .models import Booking, BookingStatus

<<<<<<< HEAD

@admin.register(BookingStatus)
class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ('booking_status_name', 'status_code')
    search_fields = ('booking_status_name',) 
    ordering = ('status_code',) 


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'patient', 'doctor', 'hospital', 'date', 'time', 'amount', 'status', 'purpose', 'type'
    )  
    list_filter = ('status', 'hospital', 'date', 'purpose', 'type')
    search_fields = ('patient__username', 'doctor__full_name', 'hospital__name')  
    date_hierarchy = 'date'
    ordering = ('-date', '-time')
    fieldsets = (
        ('تفاصيل الحجز', {
            'fields': ('patient', 'doctor', 'hospital', 'date', 'time', 'amount', 'status', 'purpose', 'type')
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')  
=======
from bookings.models import Booking
admin.site.register(Booking)
# Register your models here.
>>>>>>> 17a6cc346d6933bc45c5346f29d0bec0ec6e5923
