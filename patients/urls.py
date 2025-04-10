from django.urls import path
from .views import cancel_booking, patient_dashboard, invoice_view, appointment_details
from . import views

app_name = 'patients'

urlpatterns = [
    path('', patient_dashboard, name='patient_dashboard'),
    path('invoice/<int:payment_id>/', invoice_view, name='invoice_view'),
    path('logout/', views.user_logout, name='logout'),
    path('appointment/<int:booking_id>/', views.appointment_details, name='appointment_details'),
    path('bookings/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'),
    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
]
