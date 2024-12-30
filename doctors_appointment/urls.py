from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('', include(('home.urls', 'home'), namespace='home')),
    path('bookings/', include(('bookings.urls', 'bookings'), namespace='bookings')),
    path('payments/', include(('payments.urls', 'payments'), namespace='payments')),
    path('doctors/', include(('doctors.urls', 'doctor'), namespace='doctor')),
    path('users/', include('users.urls', namespace='users')),
    path('hospital/', include('hospitals.urls', namespace='hospitals')),
]

# إذا كانت البيئة في وضع التطوير (DEBUG = True)، يتم إضافة إعدادات خدمة الملفات الإعلامية (Media Files)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
