from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # Specialties URLs
    path('', views.index, name='specialties_list'),
    path('specialties/add/', views.specialties_create, name='specialties_add'),
    path('specialties/edit/<int:pk>/', views.specialties_update, name='specialties_edit'),
    path('specialties/delete/<int:pk>/', views.specialties_delete, name='specialties_delete'),

    # Doctors URLs
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/add/', views.doctors_create, name='doctors_add'),
    path('doctors/edit/<int:pk>/', views.doctors_update, name='doctors_edit'),
    path('doctors/delete/<int:pk>/', views.doctors_delete, name='doctors_delete'),
    path('doctors/<slug:slug>', views.doctor_detail, name='doctor_detail'),

    # Doctor Schedule URLs
    path('doctors/<int:doctor_id>/schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('doctors/<int:doctor_id>/online-booking/', views.doctor_online_booking, name='doctor_online_booking'),

    # DoctorSchedules URLs
    path('doctorschedules/', views.doctorschedules_list, name='doctorschedules_list'),
    path('doctorschedules/add/', views.doctorschedules_create, name='doctorschedules_add'),
    path('doctorschedules/edit/<int:pk>/', views.doctorschedules_update, name='doctorschedules_edit'),
    path('doctorschedules/delete/<int:pk>/', views.doctorschedules_delete, name='doctorschedules_delete'),
]
