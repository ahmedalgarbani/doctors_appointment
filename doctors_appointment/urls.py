"""
URL configuration for doctors_appointment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path


    
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from reports import views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('doctors.urls', 'doctor'), namespace='doctor')),
    path('bookings/', include(('bookings.urls', 'bookings'), namespace='doctor')),
    path('', TemplateView.as_view(template_name='frontend/home/index.html'), name='home'),
    # path('', include(('doctors.urls', 'doctor'), namespace='doctor')),
    path('users/', include('users.urls', namespace='users')),

]
