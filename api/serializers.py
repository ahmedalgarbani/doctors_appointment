from rest_framework import serializers
from django.contrib.auth.models import User
from bookings.models import Booking
from doctors.models import Doctor, DoctorPricing, DoctorSchedules, DoctorShifts,Specialty
from hospitals.models import Hospital
from django.contrib.auth import get_user_model
from django.db.models import Min, Max, Avg
from notifications.models import Notifications
from patients.models import Favourites
from payments.models import HospitalPaymentMethod, Payment, PaymentOption
from reviews.models import Review
from datetime import date

User = get_user_model()



class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "user_name","profile_picture" ,"rating", "review", "created_at"]

    def get_user_name(self, obj):
        return f"{obj.user.user.first_name} {obj.user.user.last_name}"
    
    def get_profile_picture(self, obj):
        if obj.user.user.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.user.user.profile_picture.url)
            return obj.user.user.profile_picture.url
        return None 


class SpecialtiesSerializer(serializers.ModelSerializer):
    doctors = serializers.SerializerMethodField()

    class Meta:
        model = Specialty
        fields = ['id', 'name', 'image', 'show_at_home', 'status', 'created_at', 'updated_at', 'doctors']

    def get_doctors(self, obj):
        doctors = Doctor.objects.filter(specialty=obj)
        return DoctorSerializer(doctors, many=True, context=self.context).data




class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = [
            "id",
                                "name",
                                "status",
                                "show_at_home",
                                
        ]

class DoctorShiftSerializer(serializers.ModelSerializer):
    hospital = HospitalSerializer(read_only=True)

    class Meta:
        model = DoctorShifts
        fields = ["id", "hospital", "start_time", "end_time", "available_slots", "booked_slots", "is_available"]


class DoctorScheduleSerializer(serializers.ModelSerializer):
    hospital = HospitalSerializer(read_only=True)
    day_name = serializers.SerializerMethodField()
    shifts = DoctorShiftSerializer(many=True, read_only=True)

    class Meta:
        model = DoctorSchedules
        fields = ["id", "hospital", "day", "day_name", "shifts"]

    def get_day_name(self, obj):
        return obj.get_day_display() 



class DoctorPricingSerializer(serializers.ModelSerializer):
    hospital = HospitalSerializer(read_only=True)

    class Meta:
        model = DoctorPricing
        fields = ["id", "hospital", "amount", "transaction_number"]


class DoctorSerializer(serializers.ModelSerializer):
    hospitals = HospitalSerializer(many=True, read_only=True)
    schedules = serializers.SerializerMethodField()
    pricing = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    specialty_name = serializers.SerializerMethodField()


    class Meta:
        model = Doctor
        fields = [
            "id", "created_at", "updated_at", "deleted_at",
            "full_name", "birthday", "photo","specialty","specialty_name",
            "gender",  "experience_years", "sub_title",
            "about",  "show_at_home",
            "hospitals", "schedules", "pricing",
            "reviews", "rating"
        ]

    def get_schedules(self, obj):
        schedules = DoctorSchedules.objects.filter(doctor=obj)
        return DoctorScheduleSerializer(schedules, many=True).data

    def get_pricing(self, obj):
        pricing = DoctorPricing.objects.filter(doctor=obj)
        return DoctorPricingSerializer(pricing, many=True).data
    def get_specialty_name(self, obj):
        specility = Specialty.objects.get(id=obj.specialty.id)
        return specility.name
    def get_reviews(self, obj):
        reviews = Review.objects.filter(doctor=obj, status=True)  
        return ReviewSerializer(reviews, many=True).data

    def get_rating(self, obj):
        reviews = Review.objects.filter(doctor=obj, status=True)
        if reviews.exists():
            return round(reviews.aggregate(Avg("rating"))["rating__avg"], 1) 
        return 0 





class RegisterSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'mobile_number', 'profile_picture', 'address', 'city', 'state']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        user = User.objects.create_user(**validated_data)

        if profile_picture:
            user.profile_picture = profile_picture
            user.save()

        return user
    




class FavouritesSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    doctor_data = DoctorSerializer(source='doctor', read_only=True)
    class Meta:
        model = Favourites
        fields = ['id','doctor','doctor_data']



from django.conf import settings
class BookingSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.full_name", read_only=True)
    doctorimg = serializers.SerializerMethodField()
    patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)
    hospital_name = serializers.CharField(source="hospital.name", read_only=True)
    patient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "doctor", "doctorimg", "doctor_name", "patient", "patient_name",
            "hospital", "hospital_name", "appointment_date", "appointment_time",
            "booking_date", "amount", "status", "created_at", "updated_at",
            "payment_method", "transfer_number", "payment_verified", "payment_notes"
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def validate(self, data):
        if data.get("amount") and data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return data

    def get_doctorimg(self, obj):
        request = self.context.get("request")
        if obj.doctor.photo:
            if request:
                return request.build_absolute_uri(obj.doctor.photo.url)
            return f"{settings.MEDIA_URL}{obj.doctor.photo.url}"
        return None






class PaymentOptionSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = PaymentOption
        fields = ['id', 'logo', 'method_name']

    def get_logo(self, obj):
        if obj.logo:
            request = self.context.get("request")
            print(request)
            if request:
                return request.build_absolute_uri(obj.logo.url)  
            
            return f"http://192.168.1.151:8000{obj.logo.url}"
        
        return None



class HospitalPaymentMethodSerializer(serializers.ModelSerializer):
    payment_option = PaymentOptionSerializer()
    
    class Meta:
        model = HospitalPaymentMethod
        fields = ['id','hospital','payment_option','account_name','account_number','iban','description']   





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"



class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notifications
        fields = [
            'message',  'status', 'notification_type'
        ]



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'booking', 'payment_method', 'transfer_image',
            'payment_status', 'payment_date', 'payment_subtotal',
            'payment_discount', 'payment_totalamount', 'payment_currency',
            'payment_type', 'payment_note'
        ]
        extra_kwargs = {
            'transfer_image': {'required': False, 'allow_null': True},
            'user': {'read_only': True},
            'payment_date': {'read_only': True},
            'payment_status': {'read_only': True}
        }








# ------------test-----------------
#     {
#     "username": "ya0ar932",
#     "email":"a9a0a2@a3a.com",
#     "password":"a9a1515151a",
#     "mobile_number": 781270655,
#      "birth_date":"2025-01-01",
#      "gender":"male",
#      "weight":"155",
#      "height":"165",
#      "age":"15",
#      "blood_group":"A+",
#      "first_name":"ahmed",
#      "last_name":"ali",
#      "address":"yemen",
#      "city":"sanaa",
#      "state":"LA"
# }



""" 
{
  "doctor": 1,
  "hospital": 3,
  "appointment_date": 2,
  "appointment_time": 3,
  "booking_date": "2025-12-01",
  "amount": "1933",
    "payment_method": null,
  "transfer_number": null,
    "payment_notes": null
}

{
  "id": 5,
  "doctor": 1,
  "doctorimg": "http://192.168.1.151:8000/media/doctor_images/doctor-09.jpg",
  "doctor_name": "ahmed mosa saleh",
  "patient": 2,
  "hospital": 3,
  "hospital_name": "ammar yasser",
  "appointment_date": 2,
  "appointment_time": 3,
  "booking_date": "2025-12-01",
  "amount": "1933.00",
  "is_online": false,
  "status": "pending",
  "created_at": "2025-04-04T12:40:01.536334Z",
  "updated_at": "2025-04-04T12:40:01.536334Z",
  "payment_method": null,
  "transfer_number": null,
  "payment_verified": false,
  "payment_verified_at": null,
  "payment_verified_by": null,
  "payment_notes": null
}

"""


from rest_framework import serializers
from doctors.models import Doctor, DoctorSchedules, DoctorShifts, DoctorPricing
from hospitals.models import Hospital


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorShifts
        fields = ['start_time', 'end_time', 'available_slots', 'booked_slots', 'is_available']


class ScheduleSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    shifts = ShiftSerializer(many=True, read_only=True)

    class Meta:
        model = DoctorSchedules
        fields = ['day', 'day_display', 'shifts']


class HospitalDetailSerializer(serializers.ModelSerializer):
    schedules = serializers.SerializerMethodField()
    pricing = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ['id', 'name', 'slug', 'schedules', 'pricing','logo_url']

    def get_schedules(self, hospital):
        doctor = self.context.get('doctor')
        schedules = hospital.doctor_schedules.filter(doctor=doctor)
        return ScheduleSerializer(schedules, many=True).data

    def get_pricing(self, hospital):
        doctor = self.context.get('doctor')
        pricing = doctor.pricing.filter(hospital=hospital).first()
        if pricing:
            return {
                "amount": pricing.amount,
                "transaction_number": pricing.transaction_number
            }
        
    def get_logo_url(self, hospital):
        if hospital.logo:
            return hospital.logo.url
        
        return None

