from django.urls import path,include
from . import views

app_name = 'hospitals'

urlpatterns = [
    
    
    path('', views.index, name='index'),
    path('dashboard/', views.hospital_dashboard, name='dashboard'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('doctors-filter/', views.filter_doctors, name='filter_doctors'),
    path('hospitals/blogs', views.blog_list, name='blog_list'),
    path('hospitals/pending-blogs', views.blog_pending_list, name='blog_pending_list'),
    path('hospitals/add-blog/', views.add_blog, name='add_blog'),
    path('hospitals/edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('hospitals/blogs', views.blog_list, name='blog_list'),
    path('hospitals/pending-blogs', views.blog_pending_list, name='blog_pending_list'),
    path('hospitals/add-blog/', views.add_blog, name='add_blog'),
    path('hospitals/edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('add-payment/', views.add_payment_method, name='add_payment_method'),
    path('update-payment/', views.update_payment_method, name='update_payment_method'),
    path('delete-payment/', views.delete_payment_method, name='delete_payment_method'),
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
    path('accept-appointment/<int:booking_id>/', views.accept_appointment, name='accept_appointment'),
    path('completed_appointment/<int:booking_id>/', views.completed_appointment, name='completed_appointment'),
    path('booking-history/<int:booking_id>/', views.booking_history, name='booking_history'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('schedule-timings/', views.schedule_timings, name='schedule_timings'),
    path('delete-shift/<int:shift_id>/', views.delete_shift, name='delete_shift'),
    path('filter-invoices/', views.filter_invoices, name='filter_invoices'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    



    path('accept-appointment/<int:booking_id>/', views.accept_appointment, name='accept_appointment'),
    path('completed_appointment/<int:booking_id>/', views.completed_appointment, name='completed_appointment'),
    path('booking-history/<int:booking_id>/', views.booking_history, name='booking_history'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('notifications/', include('notifications.urls',namespace='notifications'),name='notifications'),
    

    path('send-notification/', views.add_notification, name='add_notification'),

]
