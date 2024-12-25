<<<<<<< HEAD
# home/urls.py

=======
>>>>>>> 17a6cc346d6933bc45c5346f29d0bec0ec6e5923
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'home'

urlpatterns = [
<<<<<<< HEAD
    # الصفحة الرئيسية
    path('', views.index, name='home'),
    
    path('faq', views.faq_page, name='faq'),
    
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    
    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    
    path('terms-condition', views.terms_condition, name='terms_condition'),
    
=======
    path('', views.index, name='index'),
    # path('faq', views.faq_page, name='faq'),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    # path('privacy-policy',views.privacy_policy,name='privacy_policy'),
    # path('terms-condition',views.terms_condition,name='terms_condition'),
    # path('about-us',views.about_us,name='about_us'),
>>>>>>> 17a6cc346d6933bc45c5346f29d0bec0ec6e5923
    path('search/', views.search_view, name='search_view'),
    
    # صفحة عرض الأطباء (الملف الشخصي للأطباء)
    path('doctors/profile/', views.profile, name='doctors_profile'),
    
    # صفحة تفاصيل الطبيب (باستخدام ID الطبيب)
    path('doctors/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
