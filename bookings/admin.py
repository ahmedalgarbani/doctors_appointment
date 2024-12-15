from django.contrib import admin
from .models import Booking, BookingStatus


# تخصيص إدارة نموذج BookingStatus
@admin.register(BookingStatus)
class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ('booking_status_name', 'status_code')  # الحقول الظاهرة
    search_fields = ('booking_status_name',)  # الحقول القابلة للبحث
    ordering = ('status_code',)  # ترتيب السجلات


# تخصيص إدارة نموذج Booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'hospital', 'date', 'time', 'amount', 'status')  
    list_filter = ('status', 'hospital', 'date')  # تصفية حسب الحقول
    search_fields = ('patient__username', 'doctor__full_name', 'hospital__name')  
    date_hierarchy = 'date'  # شريط زمني حسب التاريخ
    ordering = ('-date', '-time')  # ترتيب الحجوزات
    fieldsets = (
        ('تفاصيل الحجز', {
            'fields': ('patient', 'doctor', 'hospital', 'date', 'time', 'amount', 'status')
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')  # منع تعديل الحقول الزمنية
