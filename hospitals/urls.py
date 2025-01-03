from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    path('', views.index, name='index'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('add-payment/', views.add_payment_method, name='add_payment_method'),
    path("toggle-payment-status/", views.toggle_payment_status, name="toggle_payment_status"),
    # path('hospitals/<int:pk>/', views.HospitalDetailView.as_view(), name='hospital_detail'),
    # path('hospital-details/<int:pk>/', views.HospitalDetailDetailView.as_view(), name='hospital_detail_detail'),
    # path('phone-numbers/', views.PhoneNumberListView.as_view(), name='phone_number_list'),
    # path('hospital-doctors/', views.HospitalDoctorListView.as_view(), name='hospital_doctor_list'),
    
    # URLs الخاصة بطلبات فتح حساب المستشفى
    path('account/request/', views.hospital_account_request, name='hospital_account_request'),
    path('account/request/success/', views.hospital_request_success, name='hospital_request_success'),
    path('account/request/<int:request_id>/status/', views.hospital_request_status, name='hospital_request_status'),
    path('hospital/<slug:slug>', views.hospital_detail, name='hospital_detail'),
]