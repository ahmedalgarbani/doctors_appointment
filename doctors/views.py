from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import Specialty, Doctor, DoctorSchedules
from .forms import SpecialtiesForm, DoctorsForm, DoctorSchedulesForm

# Index View
def index(request):
    return render(request, 'frontend/dashboard/patient/index.html')

# Specialties Views
def specialties_list(request):
    specialties = Specialty.objects.all()
    return render(request, 'frontend/dashboard/doctor/index.html', {'object_list': specialties})


def doctor_detail(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug)
    return render(request, 'frontend/home/pages/doctor_profile.html', {
        'doctor': doctor,
        'title': doctor.full_name
    })

def specialties_create(request):
    if request.method == 'POST':
        form = SpecialtiesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:specialties_list'))
    else:
        form = SpecialtiesForm()
    return render(request, 'frontend/dashboard/doctor/sections/specialties_form.html', {'form': form})

def specialties_update(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    if request.method == 'POST':
        form = SpecialtiesForm(request.POST, instance=specialty)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:specialties_list'))
    else:
        form = SpecialtiesForm(instance=specialty)
    return render(request, 'frontend/dashboard/doctor/sections/specialties_form.html', {'form': form})

def specialties_delete(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    specialty.delete()
    return HttpResponseRedirect(reverse_lazy('doctor:specialties_list'))

# Doctors Views
def doctors_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'frontend/dashboard/doctor/sections/doctor-dashboard.html', {'object_list': doctors})

def doctors_create(request):
    if request.method == 'POST':
        form = DoctorsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:doctors_list'))
    else:
        form = DoctorsForm()
    return render(request, 'frontend/dashboard/doctor/sections/doctor-dashboard.html', {'form': form})

def doctors_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorsForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:doctors_list'))
    else:
        form = DoctorsForm(instance=doctor)
    return render(request, 'frontend/dashboard/doctor/sections/doctor-dashboard.html', {'form': form})

def doctors_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.delete()
    return HttpResponseRedirect(reverse_lazy('doctor:doctors_list'))

# Doctor Schedules Views
def doctorschedules_list(request):
    schedules = DoctorSchedules.objects.all()
    return render(request, 'frontend/dashboard/doctor/sections/doctorschedules_list.html', {'object_list': schedules})

def doctorschedules_create(request):
    if request.method == 'POST':
        form = DoctorSchedulesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:doctorschedules_list'))
    else:
        form = DoctorSchedulesForm()
    return render(request, 'frontend/dashboard/doctor/sections/doctorschedules_form.html', {'form': form})

def doctorschedules_update(request, pk):
    schedule = get_object_or_404(DoctorSchedules, pk=pk)
    if request.method == 'POST':
        form = DoctorSchedulesForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:doctorschedules_list'))
    else:
        form = DoctorSchedulesForm(instance=schedule)
    return render(request, 'frontend/dashboard/doctor/sections/doctorschedules_form.html', {'form': form})

def doctorschedules_delete(request, pk):
    schedule = get_object_or_404(DoctorSchedules, pk=pk)
    schedule.delete()
    return HttpResponseRedirect(reverse_lazy('doctor:doctorschedules_list'))

# Doctor Schedule Views
def doctor_schedule(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    schedules = DoctorSchedules.objects.filter(doctor=doctor)
    
    context = {
        'doctor': doctor,
        'schedules': schedules,
    }
    return render(request, 'frontend/doctors/doctor_schedule.html', context)

def doctor_online_booking(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    schedules = DoctorSchedules.objects.filter(doctor=doctor, is_online=True)
    
    context = {
        'doctor': doctor,
        'schedules': schedules,
    }
    return render(request, 'frontend/doctors/doctor_online_booking.html', context)
from django.shortcuts import render

# Create your views here.
