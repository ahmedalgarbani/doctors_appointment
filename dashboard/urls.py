from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('hospitals/', views.hospitals_list, name='hospitals_list'),
    path('hospitals/<slug:slug>/', views.doctor_index, name='hospital_detail'),
]
