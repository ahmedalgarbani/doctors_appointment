from django.urls import path
from .views import appointments_dashboard, patients_list, patient_dashboard

app_name = 'patients'

urlpatterns = [
    path('patients/', appointments_dashboard, name='appointments_dashboard'),
    path('', patients_list, name='patients_list'),
    path('<int:patient_id>/', patient_dashboard, name='patient_dashboard'),
]
