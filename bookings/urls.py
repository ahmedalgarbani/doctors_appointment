from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('booking/<int:doctor_id>/', views.booking_view, name='booking'),
    path('get-available-slots/<int:doctor_id>/', views.get_available_slots, name='get_available_slots'),
    path('create-booking/<int:doctor_id>/', views.create_booking, name='create_booking'),
    path('payment/<int:doctor_id>/', views.payment_view, name='payment'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('appointment/<int:booking_id>/', views.appointment_details, name='appointment_details'),
    
]