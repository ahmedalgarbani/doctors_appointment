from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'home'

urlpatterns = [
    path('', views.index, name='home'),
    path('faq', views.faq_page, name='faq'),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('privacy-policy',views.privacy_policy,name='privacy_policy'),
    path('terms-condition',views.terms_condition,name='terms_condition'),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('search/', views.search_view, name='search_view'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)