from rest_framework import serializers
from django.contrib.auth.models import User
from doctors.models import Doctor, DoctorPricing, DoctorSchedules, DoctorShifts,Specialty
from hospitals.models import Hospital
from django.contrib.auth import get_user_model
from django.db.models import Min, Max, Avg
from reviews.models import Review

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


    class Meta:
        model = Doctor
        fields = [
            "id", "created_at", "updated_at", "deleted_at",
            "full_name", "birthday", "photo",
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
