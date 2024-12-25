<<<<<<< HEAD
from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Q
from .models import Booking

def dashboard_view(request):
    today = now().date()
    current_time = now().time()

    # مواعيد قادمة (أو في المستقبل)
    upcoming_bookings = Booking.objects.filter(
        Q(date__gt=today) | Q(date=today, time__gt=current_time)
    ).order_by('date', 'time')

    # مواعيد اليوم
    today_bookings = Booking.objects.filter(date=today)

    context = {
        'upcoming_bookings': upcoming_bookings,
        'today_bookings': today_bookings,
    }

    return render(request, 'frontend/dashboard/doctor/index.html', context)
=======
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from doctors.models import Doctor, DoctorSchedules
from .models import Booking
import json

# Create your views here.

@login_required
def booking_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    is_online = request.GET.get('type') == 'online'
    
    # Get available schedules for the doctor
    schedules = DoctorSchedules.objects.filter(
        doctor=doctor
    )
    
    context = {
        'doctor': doctor,
        'schedules': schedules,
        'is_online': is_online
    }
    
    return render(request, 'frontend/home/pages/booking.html', context)

@login_required
def get_available_slots(request, doctor_id):
    """API endpoint to get available slots for a specific date"""
    if request.method == 'GET':
        date = request.GET.get('date')
        is_online = request.GET.get('type') == 'online'
        
        if not date:
            return JsonResponse({'error': 'Date is required'}, status=400)
            
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # Get schedules for the specified date
        schedules = DoctorSchedules.objects.filter(
            doctor=doctor,
            day=date
        )
        
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

@login_required
def create_booking(request, doctor_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date = data.get('date')
            time = data.get('time')
            is_online = data.get('is_online', False)
            notes = data.get('notes', '')
            
            if not all([date, time]):
                return JsonResponse({
                    'error': 'Date and time are required'
                }, status=400)
            
            doctor = get_object_or_404(Doctor, id=doctor_id)
            
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
            
            # Create the booking
            booking = Booking.objects.create(
                doctor=doctor,
                patient=request.user,
                appointment_date=date,
                appointment_time=time,
                is_online=is_online,
                notes=notes
            )
            
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

@login_required
def payment_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    is_online = request.GET.get('type') == 'online'
    
    context = {
        'doctor': doctor,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'is_online': is_online
    }
    
    return render(request, 'frontend/home/pages/payment.html', context)

@login_required
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, patient=request.user)
        
        # Only allow cancellation of pending or confirmed bookings
        if booking.status not in ['pending', 'confirmed']:
            return JsonResponse({
                'error': 'Cannot cancel this booking'
            }, status=400)
        
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
>>>>>>> 17a6cc346d6933bc45c5346f29d0bec0ec6e5923
