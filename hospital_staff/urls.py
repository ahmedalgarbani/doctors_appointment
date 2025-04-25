from django.urls import path
from . import views

app_name = 'hospital_staff'

urlpatterns = [
    # صفحة إدارة الموظفين
    path('', views.staff_list, name='staff_list'),
    path('add/', views.add_staff, name='add_staff'),
    path('edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),

    # إدارة الأدوار
    path('roles/', views.role_list, name='role_list'),
    path('roles/add/', views.add_role, name='add_role'),
    path('roles/edit/<int:role_id>/', views.edit_role, name='edit_role'),
    path('roles/delete/<int:role_id>/', views.delete_role, name='delete_role'),

    # إدارة الصلاحيات
    path('permissions/', views.permission_list, name='permission_list'),

    # تغيير كلمة المرور عند أول تسجيل دخول
    path('first-login-change-password/', views.first_login_change_password, name='first_login_change_password'),
]
