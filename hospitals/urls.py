from django.urls import path,include
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'hospitals'

urlpatterns = [

    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('all/', views.all_hospitals, name='all_hospitals'),
    path('<int:hospital_id>/details/', views.hospital_details, name='hospital_details'),
    path('add-doctor-form/', views.add_doctor_form, name='add_doctor_form'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('search-doctors/', views.search_doctors, name='search_doctors'),
    path('add-existing-doctor/', views.add_existing_doctor, name='add_existing_doctor'),
    # path('dashboard/', views.hospital_dashboard, name='dashboard'),
    path('doctors-filter/', views.filter_doctors, name='filter_doctors'),
    path('doctor/<int:doctor_id>/get/', views.get_doctor, name='get_doctor'),
    path('doctor/<int:doctor_id>/update/', views.update_doctor, name='update_doctor'),
    path('doctor/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
    path('doctor/<int:doctor_id>/history/', views.get_doctor_history, name='get_doctor_history'),
    path('doctor/<int:doctor_id>/details/', views.doctor_details, name='doctor_details'),
    path('hospitals/blogs', views.blog_list, name='blog_list'),
    path('hospitals/pending-blogs', views.blog_pending_list, name='blog_pending_list'),
    path('hospitals/add-blog/', views.add_blog, name='add_blog'),
    path('hospitals/edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('hospitals/blogs', views.blog_list, name='blog_list'),
    path('hospitals/pending-blogs', views.blog_pending_list, name='blog_pending_list'),
    path('hospitals/add-blog/', views.add_blog, name='add_blog'),
    path('hospitals/edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('hospitals/blog-detail/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('add-payment/', views.add_payment_method, name='add_payment_method'),
    path('update-payment/', views.update_payment_method, name='update_payment_method'),
    path('delete-payment/', views.delete_payment_method, name='delete_payment_method'),
    path("toggle-payment-status/", views.toggle_payment_status, name="toggle_payment_status"),
    path('invoice/<int:payment_id>/', views.invoice_view, name='invoice_view'),




    # URLs الخاصة بطلبات فتح حساب المستشفى
    path('account/request/success/', views.hospital_request_success, name='hospital_request_success'),
    path('account/request/<int:request_id>/status/', views.hospital_request_status, name='hospital_request_status'),





    path('accept_appointment/<int:booking_id>/', views.accept_appointment, name='accept_appointment'),
    path('completed_appointment/<int:booking_id>/', views.completed_appointment, name='completed_appointment'),
    path('cancel_appointment/<int:booking_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('booking-history/<int:booking_id>/', views.booking_history, name='booking_history'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('schedule-timings/', views.schedule_timings, name='schedule_timings'),
    path('delete-shift/<int:shift_id>/', views.delete_shift, name='delete_shift'),
    path('filter-invoices/', views.filter_invoices, name='filter_invoices'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('update-hospital-profile/', views.update_hospital_profile, name='update_hospital_profile'),
    path('notifications/', include('notifications.urls',namespace='notifications'),name='notifications'),
    path('patients/', views.hospital_patients, name='hospital_patients'),



]
