from django.contrib import admin
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'hospital', 'status', 'start_date', 'end_date', 'views_count', 'clicks_count')
    list_filter = ('status', 'hospital')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('hospital', 'title', 'description', 'image')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Statistics', {
            'fields': ('views_count', 'clicks_count')
        }),
    )

    readonly_fields = ('views_count', 'clicks_count')
