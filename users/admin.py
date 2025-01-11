from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'mobile_number','user_type', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'gender', 'city', 'state')
    search_fields = ('username', 'email', 'mobile_number')

    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'mobile_number', 'profile_picture','user_type')}),
        ('Personal Info', {'fields': ('gender', 'is_pregnant', 'pregnancy_term', 'age', 'blood_group', 'weight', 'height')}),
        ('Family Data', {'fields': ('family_data',)}),
        ('Location', {'fields': ('city', 'state')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'mobile_number', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)