from django.urls import path, include
from . import views


name_app = 'bookings'


urlpatterns = [
    
    path('', views.index, name='bookings_index'),

]