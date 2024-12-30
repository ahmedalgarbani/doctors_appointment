from django.urls import path
from .views import appointments_dashboard

urlpatterns = [
    path('', appointments_dashboard, name='appointments_dashboard'),
    
]
