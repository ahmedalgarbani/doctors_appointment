from django.shortcuts import render
from .models import Patients, Favourites

def appointments_dashboard(request):
    patients = Patients.objects.all()
    favourites = Favourites.objects.filter(user=request.user) if request.user.is_authenticated else None

    context = {
        'patients': patients,
        'favourites': favourites,
    }
    return render(request, 'frontend/dashboard/doctor/index.html', context)
