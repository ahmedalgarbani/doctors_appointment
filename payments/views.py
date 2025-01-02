from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor, DoctorPricing, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from .models import HospitalPaymentMethod
from bookings.models import Booking
from django.http import HttpResponseBadRequest
from patients.models import Patients

# Create your views here.

@login_required
def payment_process(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # التحقق من وجود القيم المطلوبة
    day_id = request.GET.get('day')
    date_id = request.GET.get('date')
    booking_date = request.GET.get('booking_date')
    
    # التحقق من وجود جميع البيانات المطلوبة
    if not all([day_id, date_id, booking_date]):
        return HttpResponseBadRequest('يرجى اختيار اليوم والوقت وتاريخ الحجز')
    
    try:
        # التحقق من صحة المعرفات
        selected_schedule = get_object_or_404(DoctorSchedules, id=day_id, doctor=doctor)
        selected_shift = get_object_or_404(DoctorShifts, id=date_id, doctor_schedule=selected_schedule)
        
        # التحقق من توفر الموعد
        if not selected_shift.is_available:
            return HttpResponseBadRequest('عذراً، هذا الموعد غير متاح')
            
    except (ValueError, TypeError):
        return HttpResponseBadRequest('معرف اليوم أو الوقت غير صالح')
        
    is_online = request.GET.get('type') == 'online'
    
    # الحصول على المستشفى
    hospital = doctor.hospitals.first()
    if not hospital:
        return HttpResponseBadRequest('عذراً، لا يوجد مستشفى مسجل لهذا الطبيب')
    
    # الحصول على طرق الدفع النشطة للمستشفى
    payment_methods = HospitalPaymentMethod.objects.filter(hospital=hospital, is_active=True)
    if not payment_methods:
        return HttpResponseBadRequest('عذراً، لا توجد طرق دفع متاحة لهذا المستشفى')
    
    # الحصول على سعر الكشف
    try:
        pricing = DoctorPricing.objects.get(doctor=doctor, hospital=hospital)
        amount = pricing.amount
    except DoctorPricing.DoesNotExist:
        return HttpResponseBadRequest('عذراً، لم يتم تحديد سعر الكشف لهذا الطبيب')
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        transfer_number = request.POST.get('transfer_number')
        
        if not all([payment_method_id, transfer_number]):
            return HttpResponseBadRequest('يرجى اختيار طريقة الدفع وإدخال رقم الحوالة')
        
        # التحقق من طول رقم الحوالة
        if not transfer_number.isdigit() or len(transfer_number) < 5:
            return HttpResponseBadRequest('رقم الحوالة يجب أن يكون 5 أرقام على الأقل')
            
        try:
            payment_method = payment_methods.get(id=payment_method_id)
        except HospitalPaymentMethod.DoesNotExist:
            return HttpResponseBadRequest('طريقة الدفع غير صالحة')
        
        # التحقق من توفر الموعد مرة أخرى قبل الحجز
        if not selected_shift.is_available:
            return HttpResponseBadRequest('عذراً، هذا الموعد لم يعد متاحاً')
            
        # الحصول على المريض
        try:
            patient = Patients.objects.get(user=request.user)
        except Patients.DoesNotExist:
            return HttpResponseBadRequest('عذراً، لم يتم العثور على بيانات المريض')
            
        # إنشاء الحجز
        booking = Booking.objects.create(
            doctor=doctor,
            patient=patient,
            hospital=hospital,
            appointment_date=selected_schedule,
            appointment_time=selected_shift,
            booking_date=booking_date,
            is_online=is_online,
            amount=amount,
            status='pending',  # معلق حتى التحقق من الحوالة
            transfer_number=transfer_number,
            payment_method=payment_method
        )
        
        # تحديث عدد المواعيد المحجوزة
        selected_shift.booked_slots += 1
        selected_shift.save()
        
        # إعادة التوجيه إلى صفحة نجاح الحجز
        return redirect('bookings:booking_success', booking_id=booking.id)
    
    # عرض صفحة الدفع
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
