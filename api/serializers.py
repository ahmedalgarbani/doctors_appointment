from rest_framework import serializers
from django.contrib.auth.models import User
from doctors.models import Doctor
from hospitals.models import Hospital
from django.contrib.auth import get_user_model

User = get_user_model()

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'



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
