from django.contrib import admin
from .models import Specialty, Doctor, DoctorSchedules

# تخصيص واجهة إدارة Specialty
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_at_home', 'status')  # الأعمدة التي ستظهر
    list_filter = ('status', 'show_at_home')  # خيارات التصفية
    search_fields = ('name',)  # الحقول القابلة للبحث
    ordering = ('name',)  # ترتيب السجلات


# تخصيص واجهة إدارة Doctor
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'email', 'phone_number', 'status', 'show_at_home')
    list_filter = ('status', 'show_at_home', 'specialty')  # تصفية حسب الحقول
    search_fields = ('full_name', 'email', 'phone_number')  # الحقول القابلة للبحث
    filter_horizontal = ('hospitals',)  # واجهة سهلة لاختيار المستشفيات المرتبطة بالطبيب
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


# تخصيص واجهة إدارة DoctorSchedules
@admin.register(DoctorSchedules)
class DoctorSchedulesAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'hospital', 'day', 'start_time', 'end_time', 'available_slots')
    list_filter = ('day', 'hospital')  # تصفية حسب اليوم والمستشفى
    search_fields = ('doctor__full_name', 'hospital__name')  # الحقول القابلة للبحث
    ordering = ('day', 'start_time')
