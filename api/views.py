from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from doctors.models import Doctor,Specialty
from hospitals.models import Hospital
from .serializers import DoctorSerializer, HospitalSerializer, RegisterSerializer, SpecialtiesSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions
from patients.models import Patients
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser,MultiPartParser, FormParser
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.exceptions import ValidationError


User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class DoctorsViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.filter(status=True)
    serializer_class = DoctorSerializer


class SpecialtiesViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.filter(status=True)
    serializer_class = SpecialtiesSerializer


class HospitalsViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer



class RegisterView(APIView):
    parser_classes = (JSONParser,MultiPartParser, FormParser)

    def post(self, request):
        print("Received request data:", request.data)

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                print("User created:", user.username)

                required_fields = ["birth_date", "gender", "weight", "height", "age", "blood_group"]
                missing_fields = [field for field in required_fields if not request.data.get(field, None)]

                if missing_fields:
                    print("Missing patient fields:", missing_fields)
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
                    patient = Patients.objects.create(
                        user=user,
                        birth_date=birth_date,  
                        gender=request.data["gender"],
                        weight=float(request.data["weight"]),
                        height=float(request.data["height"]),
                        age=int(request.data["age"]),
                        blood_group=request.data["blood_group"],
                        notes=request.data.get("notes", "")
                    )
                except ValueError as ve:
                    print("Data conversion error:", str(ve))
                    return Response(
                        {"error": "Invalid data type for weight, height, or age."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                print("Patient created for:", patient.user.username)
                return Response({'message': 'User and patient created successfully'}, status=status.HTTP_201_CREATED)

            except ValidationError as ve:
                print("Validation Error:", str(ve))
                return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                print("Server Error:", str(e))
                return Response({'error': 'Server error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print("Serializer errors:", serializer.errors)
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
                    "mobile_number": 781270655,
                    "birth_date":patient.birth_date,
                    "gender":patient.gender,
                    "weight":patient.weight,
                    "height":patient.height,
                    "age":patient.age,
                    "blood_group":patient.blood_group,
                    "first_name":user.first_name,
                    "last_name":user.last_name,
                    "address":user.address,
                    "city":user.city,
                    "state":user.state,
                    'join_date':patient.created_at
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



# Test login
# {
#     "email":"a9a0a2@a3a.com",
#     "password":"a9a1515151a"
# }