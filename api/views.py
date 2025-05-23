from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from bookings.models import Booking
from doctors.models import Doctor,Specialty
from hospitals.models import Hospital
from notifications.models import Notifications
from payments.models import HospitalPaymentMethod, Payment
from reviews.models import Review
from .serializers import BookingSerializer, ChangePasswordSerializer, DoctorSerializer, FavouritesSerializer, HospitalPaymentMethodSerializer, HospitalSerializer, PatientSerializer, PaymentSerializer, RegisterSerializer, ReviewSerializer, SpecialtiesSerializer, UserSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions,generics
from patients.models import Favourites, Patients
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser,MultiPartParser, FormParser
from datetime import date, datetime
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .serializers import NotificationSerializer
from rest_framework.filters import SearchFilter
from .serializers import DoctorSerializer, HospitalDetailSerializer

User = get_user_model()



class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50



class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(status=True)
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        patient = Patients.objects.get(user=self.request.user)
        serializer.save(user=patient)


        
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

from django.db.models import Avg
class DoctorsViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.filter(status=True)
    serializer_class = DoctorSerializer
    filter_backends = [SearchFilter]
    filterset_fields = ['gender', 'specialty__name']
    search_fields = ['full_name', 'specialty__name']

    # فلترة الأطباء حسب الجنس، التخصص، والتقييم
    @action(detail=False, methods=['post'], url_path='filter')
    def filter_doctors(self, request):
        genders_raw = request.data.get('gender', '')
        specialties_raw = request.data.get('specialties__name', '')
        stars = request.data.get('starts', None)

        if isinstance(genders_raw, str):
            genders = [g.strip() for g in genders_raw.split(',') if g.strip()]
        else:
            genders = genders_raw or []

        if isinstance(specialties_raw, str):
            specialties = [s.strip() for s in specialties_raw.split(',') if s.strip()]
        else:
            specialties = specialties_raw or []

        gender_map = {'Male': 1, 'Female': 0}
        gender_values = [gender_map.get(g) for g in genders if gender_map.get(g) is not None]

        doctors = Doctor.objects.filter(status=True)

        if gender_values:
            doctors = doctors.filter(gender__in=gender_values)

        if specialties:
            doctors = doctors.filter(specialty__name__in=specialties)

        if stars is not None:
            try:
                stars = int(stars)
                doctors = doctors.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=stars, avg_rating__lt=stars+1)
            except ValueError:
                return Response({"error": "Invalid stars value"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(doctors, many=True)
        return Response(serializer.data)

    # إرجاع قائمة المستشفيات المرتبطة بطبيب معيّن
    @action(detail=True, methods=['get'], url_path='hospitals')
    def hospitals(self, request, pk=None):
        doctor = self.get_object()
        hospitals = doctor.hospitals.all()
        serializer = HospitalDetailSerializer(hospitals, many=True, context={'doctor': doctor})
        return Response(serializer.data)
class SpecialtiesViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.filter(status=True)
    serializer_class = SpecialtiesSerializer


class HospitalsViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer



class RegisterView(APIView):
    parser_classes = (JSONParser,MultiPartParser, FormParser)

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()

                required_fields = ["birth_date", "gender"]
                missing_fields = [field for field in required_fields if not request.data.get(field, None)]

                if missing_fields:
                    return Response(
                        {"error": "Missing required fields: " + ", ".join(missing_fields)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    birth_date_str = request.data["birth_date"].split(" ")[0]  
                    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. It must be in YYYY-MM-DD format."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    Patients.objects.create(
                        user=user,
                        birth_date=birth_date,  
                        gender=request.data["gender"],
                        notes=request.data.get("notes", "")
                    )
                except ValueError as ve:
                    return Response(
                        {"error": "Invalid data ."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                return Response({'message': 'User and patient created successfully'}, status=status.HTTP_201_CREATED)

            except ValidationError as ve:
                return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({'error': 'Server error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        device_id = request.data.get('device_id')
     
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.email, password=password)  

        if user is not None:
            tokens = get_tokens_for_user(user)
            patient = get_object_or_404(Patients,user=user)
            return Response({
                'data':{
                    'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    "mobile_number": user.mobile_number,
                    "birth_date":patient.birth_date,
                    "gender":patient.gender,
                    "first_name":user.first_name,
                    "last_name":user.last_name,
                    "address":user.address,
                    "city":user.city,
                    "state":user.state,
                    
                },
                'tokens': tokens
                }
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist() 
            
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class FavouritesViewSet(viewsets.ModelViewSet):
    serializer_class = FavouritesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Return favourites for the authenticated user."""
        patient = get_object_or_404(Patients, user=self.request.user.id)
        return Favourites.objects.filter(patient=patient)

    def perform_create(self, serializer):
        """Save favourite with the authenticated user's patient instance."""
        patient = get_object_or_404(Patients, user=self.request.user.id)
        serializer.save(patient=patient)

    def create(self, request, *args, **kwargs):
        """Handle creation of a new favourite, preventing duplicates."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = serializer.validated_data['doctor']

        patient = get_object_or_404(Patients, user=request.user.id)
        if Favourites.objects.filter(patient=patient, doctor=doctor).exists():
            return Response(
                {"detail": "Favourite already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(
            {"detail": "Favourite added successfully."},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['delete'], url_path='remove')
    def remove_favourite(self, request):
        """Remove a favourite doctor for the authenticated user."""
        doctor_id = request.data.get('doctor')

        if not doctor_id:
            return Response(
                {"error": "Doctor ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        patient = get_object_or_404(Patients, user=request.user.id)
        instance = Favourites.objects.filter(patient=patient, doctor_id=doctor_id).first()

        if instance:
            instance.delete()
            return Response(
                {"detail": "Favourite removed successfully."},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {"error": "Favourite not found."},
            status=status.HTTP_404_NOT_FOUND
        )





from django.utils import timezone
from datetime import datetime

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        patient = get_object_or_404(Patients, user=self.request.user.id)
        return Booking.objects.filter(patient=patient)

    def perform_create(self, serializer):
        patient = get_object_or_404(Patients, user=self.request.user.id)
        serializer.save(patient=patient, )

    @action(detail=False, methods=['get'])
    def history_bookings(self, request):
        patient = get_object_or_404(Patients, user=request.user.id)
        today = timezone.now().date()
        past_bookings = Booking.objects.filter(patient=patient, booking_date__lt=today)
        page = self.paginate_queryset(past_bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(past_bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming_bookings(self, request):
        patient = get_object_or_404(Patients, user=request.user.id)
        today = timezone.now().date()
        future_bookings = Booking.objects.filter(patient=patient, booking_date__gte=today)
        page = self.paginate_queryset(future_bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(future_bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_booking(self, request):
        """Creates a new booking"""
        patient = get_object_or_404(Patients, user=request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(patient=patient)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class HospitalPaymentMethodViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination

    queryset = HospitalPaymentMethod.objects.filter(is_active=True)  
    serializer_class = HospitalPaymentMethodSerializer

    @action(detail=False, methods=['post'])
    def active_payment_methods(self, request):
        hospital_id = request.data.get('hospital_id')

        if not hospital_id:
            return Response(
                {'error': 'hospital_id is required in the request body'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            hospital = Hospital.objects.get(pk=hospital_id)
        except Hospital.DoesNotExist:  
            return Response(
                {'error': 'Hospital not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        payment_methods = HospitalPaymentMethod.objects.filter(
            hospital=hospital,
            is_active=True,
            payment_option__is_active=True
        )
        serializer = HospitalPaymentMethodSerializer(payment_methods, many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # serializer = UserSerializer(request.user)
        patient = get_object_or_404(Patients,user=request.user)
        return Response({
                'result':{
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    "mobile_number": patient.user.mobile_number,
                    "birth_date":patient.birth_date,
                    "gender":patient.gender,
                    "first_name":request.user.first_name,
                    "last_name":request.user.last_name,
                    "address":request.user.address,
                    "city":request.user.city,
                    "state":request.user.state,
                },
                
            }, status=status.HTTP_200_OK)
    
    
    def put(self, request):
        try:
            user = request.user
            patient = get_object_or_404(Patients, user=user)
            data = request.data

            user_fields = ['username', 'email', 'first_name', 'last_name', 'address', 'city', 'state']
            for field in user_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            user.save()

            patient_fields = ['mobile_number', 'birth_date', 'gender']
            for field in patient_fields:
                if field in data:
                    setattr(patient, field, data[field])
            
            if 'birth_date' in data:
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                patient.age = calculate_age(birth_date)
            
            patient.save()

            return Response({'detail': 'Profile updated successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))



class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notifications.objects.filter(user=self.request.user, is_active=True)


class MarkNotificationReadView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Notifications.objects.filter(is_active=True)
    serializer_class = NotificationSerializer

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.user != request.user:
            return Response({"detail": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        notification.mark_as_read()
        return Response({"detail": "Marked as read."})


class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        updated_count = Notifications.objects.filter(user=user, status='0').update(status='1')
        return Response(
            {"detail": f"{updated_count} notifications marked as read."},
            status=status.HTTP_200_OK
        )



class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'])
    def make_payment(self, request):
        data = request.data
        required_fields = ['booking_id', 'payment_method_id', 'payment_subtotal', 'payment_currency', 'payment_type']

        for field in required_fields:
            if not data.get(field):
                return Response({'error': f'{field} is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=data['booking_id'])
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            payment_method = HospitalPaymentMethod.objects.get(id=data['payment_method_id'])
        except HospitalPaymentMethod.DoesNotExist:
            return Response({'error': 'Payment method not found'}, status=status.HTTP_404_NOT_FOUND)

        payment = Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            payment_subtotal=data['payment_subtotal'],
            payment_discount=data.get('payment_discount', 0),
            payment_currency="RYL",
            payment_type=data['payment_type'],
            payment_note=data.get('payment_note', ''),
            payment_status=0  
        )

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Test login
# {
#     "email":"a9a0a2@a3a.com",
#     "password":"a9a1515151a"
# }


# blog/api/views.py
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from blog.models import Post
from .serializers import (
    PostSerializer, 
    PostListSerializer,

)




class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(status=True).select_related(
        'author', 'categories'
    ).prefetch_related('tags')
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

