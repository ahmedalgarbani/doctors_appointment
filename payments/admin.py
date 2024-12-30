from django.contrib import admin
from .models import PaymentStatus, PaymentMethod, Payment

@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('payment_status_name', 'status_code')
    search_fields = ('payment_status_name',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('method_name', 'country', 'currency', 'activate_state')
    search_fields = ('method_name', 'country')
    list_filter = ('activate_state',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_method', 'payment_status', 'payment_date', 'payment_totalamount', 'booking')
    search_fields = ('payment_method__method_name', 'booking__guest__name')
    list_filter = ('payment_status', 'payment_type', 'payment_date')
