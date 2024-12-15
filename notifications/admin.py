from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Notifications

@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('sender', 'user', 'message', 'notification_type', 'status', 'send_time', 'is_active')
    list_filter = ('status', 'notification_type', 'is_active')
    search_fields = ('sender__username', 'user__username', 'message')
    ordering = ('-send_time',)
