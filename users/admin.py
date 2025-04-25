from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for the CustomUser model.
    """
    # Fields displayed in the list view
    list_display = ('email', 'username', 'user_type', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')  # Filters on the right
    search_fields = ('email', 'username', 'mobile_number')  # Searchable fields
    ordering = ('-date_joined',)  # Default ordering

    # Read-only fields
    readonly_fields = ('date_joined', 'last_login')

    # Fieldsets for organizing the user form in the admin interface
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_("Personal Info"), {
            'fields': ('first_name', 'last_name', 'mobile_number', 'profile_picture', 'address', 'city', 'state')
        }),
        (_("Permissions"), {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_("Important Dates"), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Fieldsets for adding a new user in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'mobile_number', 'password1', 'password2', 'user_type', 'is_active'),
        }),
    )
