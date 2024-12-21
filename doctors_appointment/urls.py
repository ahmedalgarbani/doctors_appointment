from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('bookings/', include(('bookings.urls', 'bookings'), namespace='doctor')),
    path('', TemplateView.as_view(template_name='frontend/home/index.html'), name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('hospital/', include('hospitals.urls', namespace='hospitals')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
