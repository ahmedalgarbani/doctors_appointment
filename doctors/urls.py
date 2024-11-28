# doctors/urls.py
from django.urls import path
from . import views

app_name = 'doctor'

urlpatterns = [
    path('', views.index, name='doctor_home'),

    # Specialties URLs
    path('specialties/', views.SpecialtiesListView.as_view(), name='specialties_list'),
    path('specialties/add/', views.SpecialtiesCreateView.as_view(), name='specialties_add'),
    path('specialties/edit/<int:pk>/', views.SpecialtiesUpdateView.as_view(), name='specialties_edit'),
    path('specialties/delete/<int:pk>/', views.SpecialtiesDeleteView.as_view(), name='specialties_delete'),

    # Doctors URLs
    path('doctors/', views.DoctorsListView.as_view(), name='doctors_list'),
    path('doctors/add/', views.DoctorsCreateView.as_view(), name='doctors_add'),
    path('doctors/edit/<int:pk>/', views.DoctorsUpdateView.as_view(), name='doctors_edit'),
    path('doctors/delete/<int:pk>/', views.DoctorsDeleteView.as_view(), name='doctors_delete'),

    # DoctorRates URLs
    path('doctorrates/', views.DoctorRatesListView.as_view(), name='doctorrates_list'),
    path('doctorrates/add/', views.DoctorRatesCreateView.as_view(), name='doctorrates_add'),
    path('doctorrates/edit/<int:pk>/', views.DoctorRatesUpdateView.as_view(), name='doctorrates_edit'),
    path('doctorrates/delete/<int:pk>/', views.DoctorRatesDeleteView.as_view(), name='doctorrates_delete'),

    # DoctorSchedules URLs
    path('doctorschedules/', views.DoctorSchedulesListView.as_view(), name='doctorschedules_list'),
    path('doctorschedules/add/', views.DoctorSchedulesCreateView.as_view(), name='doctorschedules_add'),
    path('doctorschedules/edit/<int:pk>/', views.DoctorSchedulesUpdateView.as_view(), name='doctorschedules_edit'),
    path('doctorschedules/delete/<int:pk>/', views.DoctorSchedulesDeleteView.as_view(), name='doctorschedules_delete'),
]
