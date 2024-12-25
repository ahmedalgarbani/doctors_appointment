from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:doctor_id>/', views.payment_process, name='process'),
]
