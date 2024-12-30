from django.contrib import admin
from .models import Reports
from django.utils.translation import gettext_lazy as _

class ReportsAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'hospital', 'created_by', 'creation_time')
    list_filter = ('report_type', 'hospital', 'created_by', 'creation_time')
    search_fields = ('report_type', 'hospital__name', 'created_by__username')
    date_hierarchy = 'creation_time'

    # تخصيص صفحة التفاصيل (تفاصيل التقرير)
    fieldsets = (
        (None, {
            'fields': ('report_type', 'hospital', 'created_by')
        }),
        (_('التفاصيل الإضافية'), {
            'fields': ('creation_time',)
        }),
    )

# تسجيل النموذج في الأدمن
admin.site.register(Reports, ReportsAdmin)
