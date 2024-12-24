from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor, DoctorPricing
from hospitals.models import Hospital
from bookings.models import Booking

# Create your views here.

@login_required
def payment_process(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    is_online = request.GET.get('type') == 'online'
    
    # الحصول على المستشفى الأول للطبيب
    hospital = doctor.hospitals.first()
    
    # الحصول على سعر الكشف
    try:
        pricing = DoctorPricing.objects.get(doctor=doctor, hospital=hospital)
        amount = pricing.amount
    except DoctorPricing.DoesNotExist:
        amount = 0
    
    if request.method == 'POST':
        # إنشاء الحجز
        booking = Booking.objects.create(
            doctor=doctor,
            patient=request.user,
            hospital=hospital,
            appointment_date=selected_date,
            appointment_time=selected_time,
            is_online=is_online,
            amount=amount,
            # payment_method=request.POST.get('payment_method', 'payment')
        )
        
        context = {
            'doctor': doctor,
            'hospital': hospital,
            'selected_date': selected_date,
            'selected_time': selected_time,
            'is_online': is_online,
            'amount': amount
        }
        
        return render(request, 'frontend/home/pages/booking-success.html', context)
    
    context = {
        'doctor': doctor,
        'hospital': hospital,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'is_online': is_online,
        'amount': amount
    }
    
    return render(request, 'frontend/home/pages/payment.html', context)
