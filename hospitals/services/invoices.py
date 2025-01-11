from payments.models import Payment

def get_invoices_with_filters(hospital, request):
    invoices = Payment.objects.filter(booking__hospital=hospital).select_related('booking', 'booking__patient')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    payment_status = request.GET.get('payment_status')
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')

    if date_from:
        invoices = invoices.filter(payment_date__gte=date_from)
    if date_to:
        invoices = invoices.filter(payment_date__lte=date_to)
    if payment_status:
        invoices = invoices.filter(payment_status_id=payment_status)
    if amount_min:
        invoices = invoices.filter(payment_totalamount__gte=amount_min)
    if amount_max:
        invoices = invoices.filter(payment_totalamount__lte=amount_max)
        
    return invoices.order_by('-payment_date')
