from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from doctors.models import Doctor, DoctorSchedules
from .models import Booking
import json

# عرض حجز الطبيب
# Create your views here.

@login_required(login_url='/user/login')

def booking_view(request, doctor_id):
  
    selected_doctor = get_object_or_404(Doctor, id=doctor_id)
    request.session['selected_doctor'] = selected_doctor
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # الحصول على الجداول المتاحة للطبيب
    # Get available schedules for the doctor
    schedules = DoctorSchedules.objects.filter(
        doctor=selected_doctor
    )
    
    context = {
        'doctor': selected_doctor,
        'schedules': schedules,
    }
    
    return render(request, 'frontend/home/pages/booking.html', context)

# الحصول على الوقت المتاح للطبيب في يوم محدد
@login_required(login_url='/user/login')

def get_available_slots(request, doctor_id):
    """نقطة النهاية API للحصول على الفترات المتاحة لليوم المحدد"""
@login_required(login_url='/user/login')

def get_available_slots(request, doctor_id):
    """API endpoint to get available slots for a specific date"""
    if request.method == 'GET':
        date = request.GET.get('date')
        
        if not date:
            return JsonResponse({'error': 'Date is required'}, status=400)
            
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # الحصول على الجداول للطبيب في اليوم المحدد
        # Get schedules for the specified date
        schedules = DoctorSchedules.objects.filter(
            doctor=doctor,
            day=date
        )
        
        # الحصول على الحجوزات الموجودة في هذا اليوم
        # Get existing bookings for the date
        existing_bookings = Booking.objects.filter(
            doctor=doctor,
            appointment_date=date
        ).values_list('appointment_time', flat=True)
        
        available_slots = []
        for schedule in schedules:
            if schedule.start_time not in existing_bookings and schedule.available_slots > 0:
                available_slots.append({
                    'time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M')
                })
        
        return JsonResponse({'slots': available_slots})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# إنشاء حجز جديد
@login_required(login_url='/user/login')

def create_booking(request, doctor_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date = data.get('date')
            time = data.get('time')
            notes = data.get('notes', '')
            
            if not all([date, time]):
                return JsonResponse({
                    'error': 'Date and time are required'
                }, status=400)
            
            doctor = get_object_or_404(Doctor, id=doctor_id)
            
            # التحقق من وجود الجدول المتاح
            # Check if slot is still available
            schedule = DoctorSchedules.objects.filter(
                doctor=doctor,
                day=date,
                start_time=time
            ).first()
            
            if not schedule or schedule.available_slots <= 0:
                return JsonResponse({
                    'error': 'This slot is no longer available'
                }, status=400)
            
            # إنشاء الحجز
            # Create the booking
            booking = Booking.objects.create(
                doctor=doctor,
                patient=request.user,
                appointment_date=date,
                appointment_time=time,
                notes=notes
            )
            
            # تقليل الفترات المتاحة
            # Decrease available slots
            schedule.available_slots -= 1
            schedule.save()
            
            return JsonResponse({
                'message': 'Booking created successfully',
                'booking_id': booking.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=405)

# عرض صفحة الدفع
@login_required(login_url='/user/login')

def payment_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    
    context = {
        'doctor': doctor,
        'selected_date': selected_date,
        'selected_time': selected_time,
    }
    
    return render(request, 'frontend/home/pages/payment.html', context)

# إلغاء الحجز
@login_required(login_url='/user/login')

def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, patient=request.user)
        
        # السماح بالإلغاء فقط للحجوزات التي هي في حالة "قيد الانتظار" أو "مؤكدة"
        # Only allow cancellation of pending or confirmed bookings
        if booking.status not in ['pending', 'confirmed']:
            return JsonResponse({
                'error': 'Cannot cancel this booking'
            }, status=400)
        
        # زيادة الفترات المتاحة مرة أخرى
        # Increase available slots back
        schedule = DoctorSchedules.objects.filter(
            doctor=booking.doctor,
            day=booking.appointment_date,
            start_time=booking.appointment_time
        ).first()
        
        if schedule:
            schedule.available_slots += 1
            schedule.save()
        
        booking.status = 'cancelled'
        booking.save()
        
        return JsonResponse({
            'message': 'Booking cancelled successfully'
        })
    
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=405)

# عرض صفحة نجاح الحجز
@login_required(login_url='/user/login')

def booking_success(request, booking_id):
    """عرض صفحة نجاح الحجز"""
    booking = get_object_or_404(Booking, id=booking_id, patient__user=request.user)
    return render(request, 'frontend/home/pages/booking_success.html', {'booking': booking})

def appointment_details(request, booking_id):
    """عرض تفاصيل الحجز في صفحة منفصلة"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    context = {
        'booking': booking,
        'page_title': 'تفاصيل الحجز'
    }
    
    return render(request, 'frontend/dashboard/hospitals/sections/appointment_details.html', context)
