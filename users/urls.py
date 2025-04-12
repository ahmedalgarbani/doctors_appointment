from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view , name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    path('signup/', TemplateView.as_view(template_name='frontend/auth/signup.html'), name='signup'),
    path('hospital-signup/', views.hospital_account_request, name='hospital_account_request'),

    path('patient-signup/', views.patient_signup, name='patient_signup'),
    path('register/step1/', views.register_step1, name='register_step1'),  
    path('register/step2/', views.register_step2, name='register_step2'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('patient-dashboard/',views.patient_dashboard, name='patient_dashboard'),
    # path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    path('change-password/', views.change_password_view, name='change_password'),


    # path('signup/', views.SignUpView.as_view(), name='signup'),
    # path('', views.IndexView.as_view(), name='index'),  # المسار الرئيسي
    # path('doctor-register/', views.doctor_register, name='doctor_register'),  # تسجيل الأطباء (مثال)
]
