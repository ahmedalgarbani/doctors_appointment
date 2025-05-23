from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, ChangePasswordView, DoctorsViewSet, FavouritesViewSet, HospitalPaymentMethodViewSet, HospitalsViewSet, LoginView, MarkAllNotificationsReadView, MarkNotificationReadView, NotificationListView, PaymentViewSet, PostViewSet, RegisterView,LogoutView, ReviewViewSet, SpecialtiesViewSet, UserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

# Test
router = DefaultRouter()
router.register(r'specialties', SpecialtiesViewSet)
router.register(r'doctors', DoctorsViewSet)
router.register(r'hospitals', HospitalsViewSet)
router.register(r'favourites', FavouritesViewSet, basename='favourite')
router.register(r'bookings', BookingViewSet,basename='booking')
router.register(r'hospital-payment-methods', HospitalPaymentMethodViewSet, basename='hospital-payment-methods')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'payment', PaymentViewSet, basename='payment')


router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),


    # notifications
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
    path('notifications/mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark-all-notifications-read'),
    
    #  JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    #  JWT authentication endpoints
    path('register/', RegisterView.as_view(), name='register'), 
    path('login/', LoginView.as_view(), name='login'),  
    path('logout/', LogoutView.as_view(), name='logout'),  


]