from django.urls import path
from . import views

app_name = 'advertisements'

urlpatterns = [
    path('list/', views.advertisement_list, name='advertisement_list'),
    path('add/', views.add_advertisement, name='add_advertisement'),
    path('edit/<int:advertisement_id>/', views.edit_advertisement, name='edit_advertisement'),
    path('delete/<int:advertisement_id>/', views.delete_advertisement, name='delete_advertisement'),
    path('detail/<int:advertisement_id>/', views.advertisement_detail, name='advertisement_detail'),
    path('load-form/', views.load_advertisement_form, name='load_advertisement_form'),
    path('load-edit-form/<int:advertisement_id>/', views.load_edit_form, name='load_edit_form'),
    path('ajax-delete/<int:advertisement_id>/', views.ajax_delete_advertisement, name='ajax_delete_advertisement'),
]
