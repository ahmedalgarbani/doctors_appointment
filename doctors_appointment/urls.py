from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
<<<<<<< HEAD
    path('bookings/', include(('bookings.urls', 'bookings'), namespace='doctor')),
    path('', include(('home.urls', 'home'), namespace='home')),
=======
    path('bookings/', include(('bookings.urls', 'bookings'), namespace='bookings')),
    path('payments/', include(('payments.urls', 'payments'), namespace='payments')),
    path('', include(('home.urls','home'),namespace='home'), name='home'),
    path('doctors/', include(('doctors.urls', 'doctor'), namespace='doctor')),
>>>>>>> 17a6cc346d6933bc45c5346f29d0bec0ec6e5923
    path('users/', include('users.urls', namespace='users')),
    path('hospital/', include('hospitals.urls', namespace='hospitals')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
