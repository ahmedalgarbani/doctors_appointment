from django.urls import path
from . import views

app_name = 'doctor'

urlpatterns = [
    path('', views.index, name='doctor_home'),

    # Specialties URLs
    path('specialties/', views.specialties_list, name='specialties_list'),
    path('specialties/add/', views.specialties_create, name='specialties_add'),
    path('specialties/edit/<int:pk>/', views.specialties_update, name='specialties_edit'),
    path('specialties/delete/<int:pk>/', views.specialties_delete, name='specialties_delete'),

    # Doctors URLs
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/add/', views.doctors_create, name='doctors_add'),
    path('doctors/edit/<int:pk>/', views.doctors_update, name='doctors_edit'),
    path('doctors/delete/<int:pk>/', views.doctors_delete, name='doctors_delete'),

    # DoctorRates URLs
    path('doctorrates/', views.doctorrates_list, name='doctorrates_list'),
    path('doctorrates/add/', views.doctorrates_create, name='doctorrates_add'),
    path('doctorrates/edit/<int:pk>/', views.doctorrates_update, name='doctorrates_edit'),
    path('doctorrates/delete/<int:pk>/', views.doctorrates_delete, name='doctorrates_delete'),

    # DoctorSchedules URLs
    path('doctorschedules/', views.doctorschedules_list, name='doctorschedules_list'),
    path('doctorschedules/add/', views.doctorschedules_create, name='doctorschedules_add'),
    path('doctorschedules/edit/<int:pk>/', views.doctorschedules_update, name='doctorschedules_edit'),
    path('doctorschedules/delete/<int:pk>/', views.doctorschedules_delete, name='doctorschedules_delete'),
]
