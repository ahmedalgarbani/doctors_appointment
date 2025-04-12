import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors_appointment.settings')
os.environ['PYTHONIOENCODING'] = 'utf-8'
django.setup()

from django.contrib.auth import get_user_model
from hospitals.models import City, Hospital, PhoneNumber
from doctors.models import Specialty, Doctor, DoctorPricing
from django.utils.text import slugify

# List of Saudi cities
saudi_cities = [
    "الرياض", "جدة", "مكة المكرمة", "المدينة المنورة", "الدمام",
    "الخبر", "الظهران", "الأحساء", "الطائف", "بريدة",
    "تبوك", "القطيف", "خميس مشيط", "الجبيل", "الخرج"
]

# List of medical specialties
specialties = [
    "طب القلب", "طب الأطفال", "طب العيون", "طب الأسنان", 
    "الجراحة العامة", "طب النساء والولادة", "طب العظام",
    "طب الأعصاب", "الطب النفسي", "طب الأنف والأذن والحنجرة",
    "طب الجلدية", "طب المسالك البولية", "طب الباطنية"
]

# List of hospital names
hospital_names = [
    "مستشفى السلام", "مستشفى الأمل", "مستشفى الحياة", "مستشفى الشفاء",
    "مستشفى النور", "مستشفى الرحمة", "مستشفى المواساة", "مستشفى دار الشفاء",
    "مستشفى الوطني", "المستشفى التخصصي", "مستشفى الملك فهد",
    "مستشفى الأمير سلطان", "مستشفى المملكة", "مستشفى السعودي الألماني"
]

# Arabic first names and last names for generating doctor names
arabic_first_names = [
    "محمد", "أحمد", "عبدالله", "عبدالرحمن", "خالد",
    "سارة", "فاطمة", "نورة", "ريم", "لينا",
    "علي", "عمر", "يوسف", "إبراهيم", "سلطان"
]

arabic_last_names = [
    "العمري", "الغامدي", "القحطاني", "السهلي", "الدوسري",
    "الشهري", "الزهراني", "المالكي", "الحربي", "السلمي",
    "العتيبي", "الشمري", "المطيري", "البقمي", "الرشيدي"
]

def create_cities():
    print("Creating cities...")
    for city_name in saudi_cities:
        try:
            City.objects.get_or_create(
                name=city_name,
                defaults={
                    'slug': slugify(city_name),
                    'status': True
                }
            )
        except Exception as e:
            print(f"Error creating city {city_name}: {e}")
    print(f"Created {len(saudi_cities)} cities")

def create_specialties():
    print("Creating specialties...")
    for specialty_name in specialties:
        Specialty.objects.get_or_create(
            name=specialty_name,
            show_at_home=True,
            status=True
        )
    print(f"Created {len(specialties)} specialties")

def create_hospitals():
    print("Creating hospitals...")
    cities = list(City.objects.all())
    User = get_user_model()
    
    for hospital_name in hospital_names:
        # Create a user for hospital manager
        username = slugify(hospital_name)
        email = f"{username}@example.com"
        
        # Create user with proper password hashing
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'user_type': 'hospital_manager',
                'is_active': True
            }
        )
        if created:
            user.set_password('defaultpassword')
            user.save()
        
        hospital, created = Hospital.objects.get_or_create(
            user=user,
            defaults={
                'name': hospital_name,
                'slug': slugify(hospital_name),
                'city': random.choice(cities),
                'description': f"مستشفى {hospital_name} هو مركز طبي متكامل يقدم خدمات صحية متميزة",
                'status': True,
                'show_at_home': True
            }
        )
        
        if created:
            # Create phone numbers for the hospital
            PhoneNumber.objects.create(
                number=f"05{random.randint(10000000, 99999999)}",
                hospital=hospital,
                phone_type='mobile'
            )
            PhoneNumber.objects.create(
                number=f"01{random.randint(1000000, 9999999)}",
                hospital=hospital,
                phone_type='landline'
            )
    
    print(f"Created {len(hospital_names)} hospitals")

def create_doctors():
    print("Creating doctors...")
    specialties_list = list(Specialty.objects.all())
    hospitals_list = list(Hospital.objects.all())
    
    for i in range(30):  # Create 30 doctors
        first_name = random.choice(arabic_first_names)
        last_name = random.choice(arabic_last_names)
        full_name = f"{first_name} {last_name}"
        
        # Generate random birthday between 30 and 60 years ago
        today = datetime.now()
        age = random.randint(30, 60)
        birthday = today - timedelta(days=age*365)
        
        doctor = Doctor.objects.create(
            full_name=full_name,
            birthday=birthday,
            phone_number=f"05{random.randint(10000000, 99999999)}",
            specialty=random.choice(specialties_list),
            gender=random.choice([Doctor.STATUS_MALE, Doctor.STATUS_FEMALE]),
            email=f"doctor{i+1}@example.com",
            experience_years=random.randint(5, 30),
            sub_title=f"استشاري {random.choice(specialties)}",
            about=f"طبيب متميز بخبرة {random.randint(5, 30)} عاماً في مجال {random.choice(specialties)}",
            status=True,
            show_at_home=True
        )
        
        # Assign random hospitals (1-2) to each doctor
        num_hospitals = min(random.randint(1, 2), len(hospitals_list))
        selected_hospitals = random.sample(hospitals_list, num_hospitals)
        doctor.hospitals.set(selected_hospitals)
        
        # Create pricing for each hospital the doctor works at
        for hospital in selected_hospitals:
            DoctorPricing.objects.create(
                doctor=doctor,
                hospital=hospital,
                amount=Decimal(random.randint(200, 800))
            )
    
    print("Created 30 doctors with their pricing")

def main():
    print("Starting database population...")
    create_cities()
    create_specialties()
    create_hospitals()
    create_doctors()
    print("Database population completed!")

if __name__ == "__main__":
    main()
