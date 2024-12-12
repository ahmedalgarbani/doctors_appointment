from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import Specialties, Doctors, DoctorRates, DoctorSchedules
from .forms import SpecialtiesForm, DoctorsForm, DoctorRatesForm, DoctorSchedulesForm


# Specialties Views
def specialties_list(request):
    specialties = Specialties.objects.all()
    return render(request, 'frontend/dashboard/doctor/index.html', {'object_list': specialties})

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
    specialty = get_object_or_404(Specialties, pk=pk)
    if request.method == 'POST':
        form = SpecialtiesForm(request.POST, instance=specialty)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:specialties_list'))
    else:
        form = SpecialtiesForm(instance=specialty)
    return render(request, 'frontend/dashboard/doctor/sections/specialties_form.html', {'form': form})

def specialties_delete(request, pk):
    specialty = get_object_or_404(Specialties, pk=pk)
    specialty.delete()
    return HttpResponseRedirect(reverse_lazy('doctor:specialties_list'))

# Doctors Views
def doctors_list(request):
    doctors = Doctors.objects.all()
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
    doctor = get_object_or_404(Doctors, pk=pk)
    if request.method == 'POST':
        form = DoctorsForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:doctors_list'))
    else:
        form = DoctorsForm(instance=doctor)
    return render(request, 'frontend/dashboard/doctor/sections/doctor-dashboard.html', {'form': form})

def doctors_delete(request, pk):
    doctor = get_object_or_404(Doctors, pk=pk)
    doctor.delete()
    return HttpResponseRedirect(reverse_lazy('doctor:doctors_list'))

# DoctorRates Views
def doctorrates_list(request):
    rates = DoctorRates.objects.all()
    return render(request, 'frontend/dashboard/doctor/sections/doctorrates_list.html', {'object_list': rates})

def doctorrates_create(request):
    if request.method == 'POST':
        form = DoctorRatesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:doctorrates_list'))
    else:
        form = DoctorRatesForm()
    return render(request, 'frontend/dashboard/doctor/sections/doctorrates_form.html', {'form': form})

def doctorrates_update(request, pk):
    rate = get_object_or_404(DoctorRates, pk=pk)
    if request.method == 'POST':
        form = DoctorRatesForm(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('doctor:doctorrates_list'))
    else:
        form = DoctorRatesForm(instance=rate)
    return render(request, 'frontend/dashboard/doctor/sections/doctorrates_form.html', {'form': form})

def doctorrates_delete(request, pk):
    rate = get_object_or_404(DoctorRates, pk=pk)
    rate.delete()
    return HttpResponseRedirect(reverse_lazy('doctor:doctorrates_list'))

# DoctorSchedules Views
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
