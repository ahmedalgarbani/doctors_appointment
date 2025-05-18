from django.urls import path
from . import views


urlpatterns = [
    path('booking-reports-data/', views.booking_reports_data, name='booking_reports_data'),
    path('booking-reports/', views.booking_reports_page, name='booking_reports_page'),
]