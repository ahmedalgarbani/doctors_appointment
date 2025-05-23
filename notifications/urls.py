from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark-unread/<int:notification_id>/', views.mark_as_unread, name='mark_as_unread'),
    path('mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),

]