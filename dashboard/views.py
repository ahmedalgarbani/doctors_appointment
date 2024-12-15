from django.shortcuts import render
# Create your views here.
from doctors.models import Specialty

def doctor_index(request):
    specialties = Specialty.objects.all()
    return render(request, 'frontend/dashboard/doctor/index.html',{
        'specialties':specialties
    })
    