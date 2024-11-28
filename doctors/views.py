# doctors/views.py
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Specialties, Doctors, DoctorRates, DoctorSchedules

def index(request):
    return render(request, 'doctors/index.html')

# Specialties Views
class SpecialtiesListView(ListView):
    model = Specialties
    template_name = 'doctors/specialties_list.html'

class SpecialtiesCreateView(CreateView):
    model = Specialties
    fields = ['specialty_name']
    template_name = 'doctors/specialties_form.html'
    success_url = reverse_lazy('doctor:specialties_list')

class SpecialtiesUpdateView(UpdateView):
    model = Specialties
    fields = ['specialty_name']
    template_name = 'doctors/specialties_form.html'
    success_url = reverse_lazy('doctor:specialties_list')

class SpecialtiesDeleteView(DeleteView):
    model = Specialties
    template_name = 'doctors/specialties_confirm_delete.html'
    success_url = reverse_lazy('doctor:specialties_list')

# Doctors Views
class DoctorsListView(ListView):
    model = Doctors
    template_name = 'doctors/doctors_list.html'

class DoctorsCreateView(CreateView):
    model = Doctors
    fields = ['name', 'hospitel_id', 'specialty_id']
    template_name = 'doctors/doctors_form.html'
    success_url = reverse_lazy('doctor:doctors_list')

class DoctorsUpdateView(UpdateView):
    model = Doctors
    fields = ['name', 'hospitel_id', 'specialty_id']
    template_name = 'doctors/doctors_form.html'
    success_url = reverse_lazy('doctor:doctors_list')

class DoctorsDeleteView(DeleteView):
    model = Doctors
    template_name = 'doctors/doctors_confirm_delete.html'
    success_url = reverse_lazy('doctor:doctors_list')

# DoctorRates Views
class DoctorRatesListView(ListView):
    model = DoctorRates
    template_name = 'doctors/doctorrates_list.html'

class DoctorRatesCreateView(CreateView):
    model = DoctorRates
    fields = ['doctor_id', 'hospitel_id', 'rate']
    template_name = 'doctors/doctorrates_form.html'
    success_url = reverse_lazy('doctor:doctorrates_list')

class DoctorRatesUpdateView(UpdateView):
    model = DoctorRates
    fields = ['doctor_id', 'hospitel_id', 'rate']
    template_name = 'doctors/doctorrates_form.html'
    success_url = reverse_lazy('doctor:doctorrates_list')

class DoctorRatesDeleteView(DeleteView):
    model = DoctorRates
    template_name = 'doctors/doctorrates_confirm_delete.html'
    success_url = reverse_lazy('doctor:doctorrates_list')

# DoctorSchedules Views
class DoctorSchedulesListView(ListView):
    model = DoctorSchedules
    template_name = 'doctors/doctorschedules_list.html'

class DoctorSchedulesCreateView(CreateView):
    model = DoctorSchedules
    fields = ['doctor_id', 'hospitel_id', 'day', 'start_time', 'end_time']
    template_name = 'doctors/doctorschedules_form.html'
    success_url = reverse_lazy('doctor:doctorschedules_list')

class DoctorSchedulesUpdateView(UpdateView):
    model = DoctorSchedules
    fields = ['doctor_id', 'hospitel_id', 'day', 'start_time', 'end_time']
    template_name = 'doctors/doctorschedules_form.html'
    success_url = reverse_lazy('doctor:doctorschedules_list')

class DoctorSchedulesDeleteView(DeleteView):
    model = DoctorSchedules
    template_name = 'doctors/doctorschedules_confirm_delete.html'
    success_url = reverse_lazy('doctor:doctorschedules_list')
