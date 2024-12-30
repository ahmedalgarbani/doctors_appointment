from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from hospitals.models import Hospital
from doctors.models import Specialty, Doctor
from patients.models import Patients, Favourites
from bookings.models import Booking
from datetime import date
from django.contrib.auth.models import User


def hospitals_list(request):
    hospitals = Hospital.objects.all()
    context = {
        'hospitals': hospitals,
    }
    return render(request, 'frontend/dashboard/doctor/sections/hospitals.html', context)

def doctor_index(request, slug):
    hospital = get_object_or_404(Hospital, slug=slug)
    
    doctors = Doctor.objects.filter(hospitals=hospital)
    
    specialties = Specialty.objects.filter(doctor__in=doctors)
    
    today = date.today()
    
    today_bookings = Booking.objects.filter(hospital=hospital, date=today).order_by('time')
    
    upcoming_bookings = Booking.objects.filter(hospital=hospital, date__gte=today).order_by('date', 'time')
    
    patients = Patients.objects.filter(user__patient_bookings__hospital=hospital).distinct()

    
    context = {
        'hospital': hospital,
        'specialties': specialties,
        'today_bookings': today_bookings,
        'upcoming_bookings': upcoming_bookings,
        'patients': patients,
    }
    
    if not today_bookings and not upcoming_bookings:
        context['no_bookings_message'] = "لا توجد حجوزات لهذا اليوم أو الأيام القادمة."
    
    return render(request, 'frontend/dashboard/doctor/index.html', context)
