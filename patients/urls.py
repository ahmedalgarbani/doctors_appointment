from django.urls import path
from .views import patient_dashboard

app_name = 'patients'

urlpatterns = [
    path('', patient_dashboard, name='patient_dashboard'),
]
