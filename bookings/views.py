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
