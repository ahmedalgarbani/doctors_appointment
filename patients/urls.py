from django.urls import path
from .views import patient_dashboard
from . import views


app_name = 'patients'

urlpatterns = [
    path('', patient_dashboard, name='patient_dashboard'),
    path('logout/', views.user_logout, name='logout'),
]
