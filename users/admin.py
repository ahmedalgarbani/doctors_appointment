from django.contrib import admin
from .models import CustomUser, Roles, Permissions, RolePermissions, Users

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'mobile_number', 'gender', 'is_pregnant', 'age', 'blood_group', 'city', 'state')
    search_fields = ('username', 'email', 'mobile_number')
    list_filter = ('gender', 'is_pregnant', 'blood_group')

admin.site.register(CustomUser, CustomUserAdmin)

class RolesAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'role_desc')
    search_fields = ('role_name',)

admin.site.register(Roles, RolesAdmin)

class PermissionsAdmin(admin.ModelAdmin):
    list_display = ('permission_name', 'permission_code')
    search_fields = ('permission_name',)

admin.site.register(Permissions, PermissionsAdmin)

class RolePermissionsAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    search_fields = ('role__role_name', 'permission__permission_name')
    list_filter = ('role', 'permission')

admin.site.register(RolePermissions, RolePermissionsAdmin)

class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'role')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('role',)

admin.site.register(Users, UsersAdmin)
