from django.contrib import admin
from .models import RegistrationRequests
from django.utils.translation import gettext_lazy as _

class RegistrationRequestsAdmin(admin.ModelAdmin):
    # الحقول التي سيتم عرضها في واجهة الأدمن
    list_display = ('hotel_name', 'full_name', 'status', 'application_date', 'verify_number', 'review_date', 'reviewer')
    
    # إضافة فلاتر لتصفية البيانات
    list_filter = ('status', 'application_date', 'review_date', 'reviewer')
    
    # إضافة حقل بحث
    search_fields = ('hotel_name', 'full_name', 'verify_number', 'email')
    
    # تخصيص طريقة عرض حالة الطلب
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = _('حالة الطلب')

    # إضافة حقل للتعديل السريع (list edit)
    list_editable = ('status',)

    # إضافة خاصية تنسيق التاريخ
    date_hierarchy = 'application_date'

    # تخصيص الصفحة عند عرض التفاصيل
    fieldsets = (
        (None, {
            'fields': ('hotel_name', 'full_name', 'email', 'phone', 'business_license_number', 'document_path', 'verify_number', 'verify_code')
        }),
        (_('التفاصيل الإدارية'), {
            'fields': ('status', 'admin_notes', 'review_date', 'reviewer', 'notes'),
        }),
        (_('معلومات الحظر'), {
            'fields': ('block_end',)
        }),
    )

    # إضافة خاصية تحديث حالة الطلب (موافقة أو رفض)
    actions = ['approve_request', 'reject_request']

    def approve_request(self, request, queryset):
        queryset.update(status=RegistrationRequests.STATUS_APPROVED)
        self.message_user(request, _('تمت الموافقة على الطلبات المحددة'))

    def reject_request(self, request, queryset):
        queryset.update(status=RegistrationRequests.STATUS_REJECTED)
        self.message_user(request, _('تم رفض الطلبات المحددة'))

    approve_request.short_description = _('موافقة على الطلبات المحددة')
    reject_request.short_description = _('رفض الطلبات المحددة')

# تسجيل النموذج في الأدمن
admin.site.register(RegistrationRequests, RegistrationRequestsAdmin)
