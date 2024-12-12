from django.contrib import admin
from .models import Users, Roles, Permissions, RolePermissions

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'role']

@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ['role_name', 'role_desc']

@admin.register(Permissions)
class PermissionsAdmin(admin.ModelAdmin):
    list_display = ['permission_name', 'permission_code']

@admin.register(RolePermissions)
class RolePermissionsAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission']
