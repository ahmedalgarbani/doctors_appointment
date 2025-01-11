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
    list_display = ('full_name','gender', 'specialty', 'email', 'phone_number', 'status', 'show_at_home')
    list_filter = ('status', 'show_at_home', 'specialty')
    search_fields = ('full_name', 'email', 'phone_number','gender')
    filter_horizontal = ('hospitals',)
    ordering = ('full_name',)
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('full_name', 'birthday', 'phone_number', 'email', 'photo','gender')
        }),
        ('المستشفيات والتخصصات', {
            'fields': ('hospitals', 'specialty', 'sub_title', 'about')
        }),
        ('الإعدادات', {
            'fields': ('status', 'show_at_home')
        }),
    )



@admin.register(DoctorSchedules)
class DoctorSchedulesAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'hospital', 'get_day_display')
    list_filter = ('doctor', 'hospital', 'day')
    search_fields = ('doctor__full_name', 'hospital__name')
    ordering = ('day', 'doctor')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # إذا كنا نقوم بتحرير جدول موجود
            form.base_fields['doctor'].disabled = True
            form.base_fields['day'].disabled = True
        return form


@admin.register(DoctorShifts)
class DoctorShiftsAdmin(admin.ModelAdmin):
    list_display = ('doctor_schedule', 'start_time', 'end_time', 'available_slots', 'booked_slots', 'is_available')
    list_filter = ('doctor_schedule__doctor', 'doctor_schedule__day')
    search_fields = ('doctor_schedule__doctor__full_name',)
    ordering = ('doctor_schedule', 'start_time')
    
    def is_available(self, obj):
        return obj.available_slots > obj.booked_slots
    is_available.boolean = True
    is_available.short_description = 'متاح'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # إذا كنا نقوم بتحرير موعد موجود
            form.base_fields['doctor_schedule'].disabled = True
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # إذا كنا نقوم بإنشاء موعد جديد
            # التحقق من تداخل المواعيد
            overlapping = DoctorShifts.objects.filter(
                doctor_schedule=obj.doctor_schedule,
                start_time__lt=obj.end_time,
                end_time__gt=obj.start_time
            )
            if overlapping.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError('يوجد تداخل مع موعد آخر في نفس اليوم')
        super().save_model(request, obj, form, change)


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
