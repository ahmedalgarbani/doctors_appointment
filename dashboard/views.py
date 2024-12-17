from django.shortcuts import render
<<<<<<< HEAD
# Create your views here.
from doctors.models import Specialty

def doctor_index(request):
    specialties = Specialty.objects.all()
    return render(request, 'frontend/dashboard/doctor/index.html',{
        'specialties':specialties
    })
    
=======

# Create your views here.
>>>>>>> 98ca75c130f9cf6c22b7c0b3a95afd4a294c4972
