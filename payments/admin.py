from django.contrib import admin
from .models import  Payment, PaymentOption, HospitalPaymentMethod
from django.utils.translation import gettext_lazy as _


# ------------PaymentOption Admin-------------
@admin.register(PaymentOption)
class PaymentOptionAdmin(admin.ModelAdmin):
    list_display = ['method_name', 'currency', 'is_active']
    list_filter = ['is_active']
    search_fields = ['method_name']

# ------------HospitalPaymentMethod Admin-------------
@admin.register(HospitalPaymentMethod)
class HospitalPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'payment_option', 'account_name', 'is_active']
    list_filter = ['hospital', 'payment_option', 'is_active']
    search_fields = ['hospital__name', 'payment_option__method_name', 'account_name']

# ------------Payment Admin-------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'payment_method', 'payment_status', 'payment_date', 'payment_totalamount', 'payment_type']
    list_filter = ['payment_status', 'payment_type', 'payment_date']
    search_fields = ['booking__patient__full_name', 'payment_method__payment_option__method_name']
    readonly_fields = ['payment_date']
    fieldsets = (
        ('معلومات الحجز', {
            'fields': ('booking', 'payment_method', 'payment_status')
        }),
        ('معلومات الدفع', {
            'fields': ('payment_type', 'payment_subtotal', 'payment_discount', 'payment_totalamount', 'payment_currency')
        }),
        ('معلومات إضافية', {
            'fields': ('payment_date', 'payment_note')
        }),
    )
