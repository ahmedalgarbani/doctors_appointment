from django.db.models import Sum
from doctors.models import Specialty
from payments.models import Payment


def get_specialties_percentage(hospital):
    specialties = Specialty.objects.filter(doctor__hospitals=hospital).distinct()
    total_specialties = specialties.count()
    return min((total_specialties / 10) * 100, 100), specialties

def get_monthly_revenue(hospital, today):
    return Payment.objects.filter(
        booking__hospital=hospital,
        payment_date__year=today.year,
        payment_date__month=today.month,
        payment_status__status_code=2
    ).aggregate(total=Sum('payment_totalamount'))['total'] or 0

def get_revenue_percentage(monthly_revenue, target=50000):
    return min((monthly_revenue / target) * 100, 100)
