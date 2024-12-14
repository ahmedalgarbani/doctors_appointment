
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name='dashboard'

urlpatterns = [
       path('doctor', views.doctor_index, name='doctor_index'),

    

]
