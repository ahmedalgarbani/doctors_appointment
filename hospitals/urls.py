from django.urls import path
from . import views

urlpatterns = [
    
    path('hospitals/', views.HospitalListView.as_view(), name='hospital_list'),
    path('hospitals/<int:pk>/', views.HospitalDetailView.as_view(), name='hospital_detail'),
    path('hospital-details/<int:pk>/', views.HospitalDetailDetailView.as_view(), name='hospital_detail_detail'),
    path('phone-numbers/', views.PhoneNumberListView.as_view(), name='phone_number_list'),
    path('hospital-doctors/', views.HospitalDoctorListView.as_view(), name='hospital_doctor_list'),
]