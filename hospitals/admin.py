from django.contrib import admin
from .models import Hospital, HospitalDetail, PhoneNumber

admin.site.register(Hospital)
admin.site.register(HospitalDetail)
admin.site.register(PhoneNumber)
