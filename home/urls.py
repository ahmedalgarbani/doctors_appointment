# home/urls.py

from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from payments.views import payment_process

app_name = 'home'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.index, name='home'),
    
    path('faq', views.faq_page, name='faq'),
    
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('privacy-policy',views.privacy_policy,name='privacy_policy'),
    path('terms-condition',views.terms_condition,name='terms_condition'),
    path('search/', views.search_view, name='search_view'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('booking/<int:doctor_id>/', views.booking_view, name='booking'),
    path('get-time-slots/<int:schedule_id>/<int:doctor_id>/', views.get_time_slots, name='get_time_slots'),
    path('payment/<int:doctor_id>/', payment_process, name='payment'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
