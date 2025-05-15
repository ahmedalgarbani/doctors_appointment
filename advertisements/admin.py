from django.contrib import admin
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'hospital', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'hospital')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('hospital', 'title', 'description')
        }),
        ('Images', {
            'fields': ('image', 'image2', 'image3', 'image4'),
            'classes': ('collapse',),
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'status')
        }),
    )

    readonly_fields = ()
