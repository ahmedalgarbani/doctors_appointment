from django.shortcuts import render
from django.utils.timezone import now
from doctors.models import Specialty
from patients.models import Patients, Favourites
from bookings.models import Booking
from datetime import date
from django.contrib.auth.models import User

def doctor_index(request):
    specialties = Specialty.objects.all()
    patients = Patients.objects.all()
    favourites = Favourites.objects.all()

    today = date.today()
    today_bookings = Booking.objects.filter(date=today).order_by('time')
    upcoming_bookings = Booking.objects.filter(date__gte=date.today()).order_by('date', 'time')

    print(f"Today Bookings: {today_bookings}")
    print(f"Upcoming Bookings: {upcoming_bookings}")

    context = {
        'specialties': specialties,
        'patients': patients,
        'favourites': favourites,
        'upcoming_bookings': upcoming_bookings,
        'today_bookings': today_bookings,
    }

    return render(request, 'frontend/dashboard/doctor/index.html', context)
