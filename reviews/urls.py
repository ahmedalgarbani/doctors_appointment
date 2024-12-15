from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from django.urls import path
from . import views

urlpatterns = [
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:review_id>/', views.review_detail, name='review_detail'),
    path('reviews/create/', views.review_create, name='review_create'),
    path('reviews/<int:review_id>/update/', views.review_update, name='review_update'),
    path('reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
