from django.contrib import admin
from .models import PaymentStatus, PaymentMethod, ChoosePayment, Payment
from django.utils.translation import gettext_lazy as _

# ------------PaymentStatus Admin-------------
@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('payment_status_name', 'status_code')
    search_fields = ('payment_status_name', 'status_code')
    list_filter = ('status_code',)
    ordering = ('status_code',)

# ------------PaymentMethod Admin-------------
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('method_name', 'activate_state', 'country', 'currency', 'logo')
    search_fields = ('method_name', 'country', 'currency')
    list_filter = ('activate_state', 'country')
    ordering = ('-activate_state', 'method_name')

# ------------ChoosePayment Admin-------------
@admin.register(ChoosePayment)
class ChoosePaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_option', 'status', 'account_number')
    search_fields = ('payment_option__method_name', 'account_number')
    list_filter = ('status',)
    ordering = ('-status',)

# ------------Payment Admin-------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_choose', 'payment_status', 'payment_date', 'payment_totalamount', 'payment_currency', 'payment_type')
    search_fields = ('payment_choose__payment_option__method_name', 'payment_status__payment_status_name', 'payment_currency', 'payment_type')
    list_filter = ('payment_choose', 'payment_status', 'payment_type', 'payment_currency')
    ordering = ('-payment_date',)

    def has_add_permission(self, request):
        # Optionally restrict adding new payments directly from the admin
        return True
