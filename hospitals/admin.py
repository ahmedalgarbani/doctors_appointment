from django.contrib import admin
from .models import Hospitals, HospitalDetail, PhoneNumber, HospitalDoctor

admin.site.register(Hospitals)
admin.site.register(HospitalDetail)
admin.site.register(PhoneNumber)
admin.site.register(HospitalDoctor)
