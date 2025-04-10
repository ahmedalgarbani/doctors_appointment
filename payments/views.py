from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor, DoctorPricing, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from .models import HospitalPaymentMethod, Payment
from bookings.models import Booking
from django.http import HttpResponseBadRequest
from patients.models import Patients

# Create your views here.

def payment_process(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # Verify required values
    if request.method == 'POST':
        day_id = request.POST.get('day')
        date_id = request.POST.get('date')
        booking_date = request.POST.get('booking_date')
        hospital_id = request.POST.get('hospital_id')
    else:
        day_id = request.GET.get('day')
        date_id = request.GET.get('date')
        booking_date = request.GET.get('booking_date')
        hospital_id = request.GET.get('hospital_id')
    
    print("Day ID:", day_id)
    print("Date ID:", date_id)
    print("Booking Date:", booking_date)
    print("Hospital ID:", hospital_id)
    
    if not all([day_id, date_id, booking_date, hospital_id]):
        return HttpResponseBadRequest('يرجى اختيار اليوم والوقت وتاريخ الحجز والمستشفى')
    
    try:
        # Get hospital and validate it's associated with the doctor
        selected_hospital = get_object_or_404(Hospital, id=hospital_id)
        if not doctor.hospitals.filter(id=hospital_id).exists():
            return HttpResponseBadRequest('المستشفى المختار غير مرتبط بالطبيب')
            
        # Get doctor's price for this hospital
        doctor_price = DoctorPricing.objects.filter(DoctorPricing, doctor=doctor, hospital=selected_hospital)
        
        # Validate schedule and shift IDs
        selected_schedule = get_object_or_404(DoctorSchedules, id=day_id, doctor=doctor)
        selected_shift = get_object_or_404(DoctorShifts, id=date_id, doctor_schedule=selected_schedule)
        
        # Check if the appointment is available
        if not selected_shift.is_available:
            return HttpResponseBadRequest('عذراً، هذا الموعد غير متاح')
            
    except (ValueError, TypeError):
        return HttpResponseBadRequest('معرف اليوم أو الوقت غير صالح')
    
    is_online = request.GET.get('type') == 'online'
    
    # Get payment methods
    payment_methods = HospitalPaymentMethod.objects.filter(hospital=selected_hospital, is_active=True)
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        transfer_number = request.POST.get('transfer_number')
        notes = request.POST.get('notes', '')
        
        print("POST request received")
        print("Payment method:", payment_method_id)
        print("Transfer number:", transfer_number)
        
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
            hospital=selected_hospital,
            appointment_date=selected_schedule,
            appointment_time=selected_shift,
            booking_date=booking_date,
            is_online=is_online,
            amount=doctor_price.amount,
            status='pending',  
            transfer_number=transfer_number,
            payment_method=payment_method
        )
        
        # Create the payment
        subtotal = float(request.POST.get('subtotal', doctor_price.amount))
        discount = float(request.POST.get('discount', 0))
        total = subtotal - discount
        
        Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            payment_status=0,
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
    
    context = {
        'doctor': doctor,
        'hospital_id':hospital_id,
        'selected_hospital': selected_hospital,
        'doctor_price': doctor_price,
        'selected_schedule': selected_schedule,
        'selected_shift': selected_shift,
        'booking_date': booking_date,
        'is_online': is_online,
        'payment_methods': payment_methods
    }
    
    return render(request, 'frontend/home/pages/payment.html', context)
