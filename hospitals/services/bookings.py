from bookings.models import Booking

def get_appointments_stats(bookings, today):
    total_appointments = bookings.filter(
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    appointments_target = 100
    appointments_percentage = min((total_appointments / appointments_target) * 100, 100)
    return total_appointments, appointments_percentage