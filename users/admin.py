from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Roles, Permissions, RolePermissions, Users

# تخصيص عرض CustomUser في لوحة الإدارة
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'mobile_number', 'user_type', 'is_staff', 'is_active', 'gender', 'is_pregnant', 'age', 'blood_group', 'city', 'state')
    list_filter = ('is_staff', 'is_active', 'gender', 'is_pregnant', 'blood_group', 'city', 'state')
    search_fields = ('username', 'email', 'mobile_number')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('mobile_number', 'profile_picture', 'gender', 'is_pregnant', 'pregnancy_term', 'weight', 'height', 'age', 'blood_group', 'family_data', 'city', 'state')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'user_type', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'mobile_number', 'password1', 'password2', 'user_type', 'is_active', 'is_staff'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# تخصيص عرض Roles في لوحة الإدارة
class RolesAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'role_desc')
    search_fields = ('role_name',)

admin.site.register(Roles, RolesAdmin)

# تخصيص عرض Permissions في لوحة الإدارة
class PermissionsAdmin(admin.ModelAdmin):
    list_display = ('permission_name', 'permission_code')
    search_fields = ('permission_name',)

admin.site.register(Permissions, PermissionsAdmin)

# تخصيص عرض RolePermissions في لوحة الإدارة
class RolePermissionsAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    search_fields = ('role__role_name', 'permission__permission_name')
    list_filter = ('role', 'permission')

admin.site.register(RolePermissions, RolePermissionsAdmin)

# تخصيص عرض Users في لوحة الإدارة
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'role')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('role',)

admin.site.register(Users, UsersAdmin)
