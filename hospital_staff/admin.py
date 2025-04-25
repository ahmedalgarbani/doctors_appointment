from django.contrib import admin
from .models import StaffPermission, StaffRole, HospitalStaff, StaffAdditionalPermission

@admin.register(StaffPermission)
class StaffPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'description')
    search_fields = ('name', 'codename')
    ordering = ('name',)

@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'hospital', 'is_default')
    list_filter = ('hospital', 'is_default')
    search_fields = ('name', 'hospital__name')
    filter_horizontal = ('permissions',)
    ordering = ('hospital', 'name')

@admin.register(HospitalStaff)
class HospitalStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital', 'role', 'job_title', 'status', 'hire_date')
    list_filter = ('hospital', 'role', 'status')
    search_fields = ('user__username', 'user__email', 'job_title')
    ordering = ('hospital', 'user')
    date_hierarchy = 'hire_date'

@admin.register(StaffAdditionalPermission)
class StaffAdditionalPermissionAdmin(admin.ModelAdmin):
    list_display = ('staff', 'permission', 'granted')
    list_filter = ('granted', 'permission')
    search_fields = ('staff__user__username', 'permission__name')
    ordering = ('staff', 'permission')
