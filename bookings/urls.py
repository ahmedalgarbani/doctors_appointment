from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('booking/<int:doctor_id>/', views.booking_view, name='booking'),
    path('payment/<int:doctor_id>/', views.payment_view, name='payment'),
    path('api/slots/<int:doctor_id>/', views.get_available_slots, name='get_slots'),
    path('api/create/<int:doctor_id>/', views.create_booking, name='create'),
    path('api/cancel/<int:booking_id>/', views.cancel_booking, name='cancel'),
    path('success/<int:booking_id>/', views.booking_success, name='booking_success'),
]