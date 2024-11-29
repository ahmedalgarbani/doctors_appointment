from django.contrib import admin
from .models import Doctors, Specialties, DoctorRates, DoctorSchedules

admin.site.register(Doctors)
admin.site.register(Specialties)
admin.site.register(DoctorRates)
admin.site.register(DoctorSchedules)
