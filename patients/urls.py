from django.urls import path
from .views import patient_dashboard, invoice_view
from . import views

app_name = 'patients'

urlpatterns = [
    path('', patient_dashboard, name='patient_dashboard'),
    path('invoice/<int:payment_id>/', invoice_view, name='invoice_view'),
    path('logout/', views.user_logout, name='logout'),
]