from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor, DoctorPricing, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from .models import HospitalPaymentMethod, Payment, PaymentStatus
from bookings.models import Booking
from django.http import HttpResponseBadRequest
from patients.models import Patients

# Create your views here.
@login_required(login_url='/user/login')

def payment_process(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # Verify required values
    day_id = request.GET.get('day')
    date_id = request.GET.get('date')
    booking_date = request.GET.get('booking_date')
    
    if not all([day_id, date_id, booking_date]):
        return HttpResponseBadRequest('يرجى اختيار اليوم والوقت وتاريخ الحجز')
    
    try:
        # Validate schedule and shift IDs
        selected_schedule = get_object_or_404(DoctorSchedules, id=day_id, doctor=doctor)
        selected_shift = get_object_or_404(DoctorShifts, id=date_id, doctor_schedule=selected_schedule)
        
        # Check if the appointment is available
        if not selected_shift.is_available:
            return HttpResponseBadRequest('عذراً، هذا الموعد غير متاح')
            
    except (ValueError, TypeError):
        return HttpResponseBadRequest('معرف اليوم أو الوقت غير صالح')
    
    is_online = request.GET.get('type') == 'online'
    
    # Get the hospital
    hospital = doctor.hospitals.first()
    if not hospital:
        return HttpResponseBadRequest('عذراً، لا يوجد مستشفى مسجل لهذا الطبيب')
    
    # Fetch active payment methods for the hospital
    payment_methods = HospitalPaymentMethod.objects.filter(hospital=hospital, is_active=True)
    if not payment_methods:
        return HttpResponseBadRequest('عذراً، لا توجد طرق دفع متاحة لهذا المستشفى')
    
    # Get doctor pricing
    try:
        pricing = DoctorPricing.objects.get(doctor=doctor, hospital=hospital)
        amount = pricing.amount
    except DoctorPricing.DoesNotExist:
        return HttpResponseBadRequest('عذراً، لم يتم تحديد سعر الكشف لهذا الطبيب')
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        transfer_number = request.POST.get('transfer_number')
        notes = request.POST.get('notes', '')
        
        if not all([payment_method_id, transfer_number]):
            return HttpResponseBadRequest('يرجى اختيار طريقة الدفع وإدخال رقم الحوالة')
        
        # Validate transfer number
        if not transfer_number.isdigit() or len(transfer_number) < 5:
            return HttpResponseBadRequest('رقم الحوالة يجب أن يكون 5 أرقام على الأقل')
            
        try:
            payment_method = payment_methods.get(id=payment_method_id)
        except HospitalPaymentMethod.DoesNotExist:
            return HttpResponseBadRequest('طريقة الدفع غير صالحة')
        
        # Re-check appointment availability
        if not selected_shift.is_available:
            return HttpResponseBadRequest('عذراً، هذا الموعد لم يعد متاحاً')
            
        # Get the patient
        try:
            patient = Patients.objects.get(user=request.user)
        except Patients.DoesNotExist:
            return HttpResponseBadRequest('عذراً، لم يتم العثور على بيانات المريض')
            
        # Create the booking
        booking = Booking.objects.create(
            doctor=doctor,
            patient=patient,
            hospital=hospital,
            appointment_date=selected_schedule,
            appointment_time=selected_shift,
            booking_date=booking_date,
            is_online=is_online,
            amount=amount,
            status='pending',  # Pending until transfer verification
            transfer_number=transfer_number,
            payment_method=payment_method
        )
        
        # Create the payment
        subtotal = float(request.POST.get('subtotal', amount))
        discount = float(request.POST.get('discount', 0))
        total = subtotal - discount
        
        Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            payment_status=get_object_or_404(PaymentStatus, status_code=1),  # Default: pending
            payment_subtotal=subtotal,
            payment_discount=discount,
            payment_totalamount=total,
            payment_currency=payment_method.payment_option.currency,
            payment_note=notes,
            payment_type='e_pay' if is_online else 'cash'
        )
        
        # # Update shift's booked slots
        # selected_shift.booked_slots += 1
        # selected_shift.save()
        
        # Redirect to booking success page
        return redirect('bookings:booking_success', booking_id=booking.id,)
    
    # Render payment page
    context = {
        'doctor': doctor,
        'hospital': hospital,
        'schedule': selected_schedule,
        'shift': selected_shift,
        'booking_date': booking_date,
        'amount': amount,
        'is_online': is_online,
        'payment_methods': payment_methods
    }
    
    return render(request, 'frontend/home/pages/payment.html', context)

pass
