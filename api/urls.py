from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorsViewSet, HospitalsViewSet, LoginView, RegisterView,LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

# Test
router = DefaultRouter()
router.register(r'doctors', DoctorsViewSet)
router.register(r'hospitals', HospitalsViewSet)

urlpatterns = [
    
    path('', include(router.urls)),

    #  JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    #  JWT authentication endpoints
    path('register/', RegisterView.as_view(), name='register'), 
    path('login/', LoginView.as_view(), name='login'),  
    path('logout/', LogoutView.as_view(), name='logout'),  
]
