import os
import django
import random
from datetime import time, datetime
from django.db import utils as django_db_utils

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors_appointment.settings')
django.setup()

# Import models
from users.models import CustomUser
from doctors.models import Specialty, Doctor, DoctorSchedules, DoctorShifts, DoctorPricing
from hospitals.models import City, Hospital

def create_cities():
    print("Creating cities...")
    city_names = ['الرياض', 'جدة', 'الدمام', 'مكة المكرمة', 'المدينة المنورة']
    cities = []
    for name in city_names:
        city, created = City.objects.get_or_create(
            name=name,
            slug=name.replace(' ', '-'),
            status=True
        )
        cities.append(city)
    return cities

def create_admin_user():
    print("Creating admin user...")
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        email='admin@example.com',
        defaults={
            'user_type': 'admin',
            'mobile_number': '0500000000',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    return admin_user

def create_hospital_users():
    print("Creating hospital users...")
    users = []
    for i in range(5):
        email = f'hospital{i}@example.com'
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': f'hospital_manager_{i}',
                'user_type': 'hospital_manager',
                'mobile_number': f'05{str(random.randint(10000000, 99999999))}',
                'address': f'عنوان {i}',
                'city': 'الرياض',
                'state': 'الرياض',
            }
        )
        if created:
            user.set_password('hospital123')
            user.save()
        users.append(user)
    return users

def create_hospitals(hospital_users):
    print("Creating hospitals...")
    hospitals = []
    hospital_names = [
        'مستشفى المملكة',
        'مستشفى السلام',
        'مستشفى الأمل',
        'مستشفى الرحمة',
        'مستشفى الشفاء'
    ]
    for i, user in enumerate(hospital_users):
        hospital, created = Hospital.objects.get_or_create(
            user=user,
            defaults={
                'name': hospital_names[i],
                'slug': f'hospital-{i}',
                'description': 'وصف المستشفى',
                'sub_title': 'عنوان فرعي للمستشفى',
                'about': 'نبذة عن المستشفى',
                'status': True,
                'show_at_home': True,
                'created_by': user
            }
        )
        hospitals.append(hospital)
    return hospitals

def create_specialties():
    print("Creating specialties...")
    specialty_names = [
        'طب القلب',
        'طب الأطفال',
        'طب العيون',
        'طب الأسنان',
        'طب النساء والولادة',
        'طب العظام',
        'طب الباطنية',
        'طب الجلدية'
    ]
    specialties = []
    for name in specialty_names:
        specialty, created = Specialty.objects.get_or_create(
            name=name,
            defaults={
                'show_at_home': True,
                'status': True
            }
        )
        specialties.append(specialty)
    return specialties

def create_doctors(specialties, hospitals):
    print("Creating doctors...")
    doctors = []
    doctor_names = [
        'د. أحمد محمد',
        'د. محمد علي',
        'د. خالد عبدالله',
        'د. عبدالرحمن سعد',
        'د. فهد ناصر',
        'د. سارة أحمد',
        'د. نورة محمد',
        'د. فاطمة علي',
        'د. عائشة خالد',
        'د. ريم سعد'
    ]
    
    for i, name in enumerate(doctor_names):
        email = f'doctor{i}@example.com'
        doctor, created = Doctor.objects.get_or_create(
            email=email,
            defaults={
                'full_name': name,
                'birthday': datetime(1980 + i % 20, 1 + i % 12, 1 + i % 28),
                'phone_number': f'05{str(random.randint(10000000, 99999999))}',
                'specialty': random.choice(specialties),
                'gender': random.choice([0, 1]),
                'experience_years': random.randint(1, 30),
                'sub_title': f'أخصائي {random.choice(specialties).name}',
                'about': f'نبذة عن الدكتور {name}',
                'status': True,
                'show_at_home': random.choice([True, False])
            }
        )
        
        if created:
            # Add random hospitals to doctor
            selected_hospitals = random.sample(list(hospitals), random.randint(1, min(3, len(hospitals))))
            doctor.hospitals.set(selected_hospitals)
            
            # Create schedules for each hospital
            for hospital in selected_hospitals:
                # Create random schedules for different days
                available_days = list(range(7))  # 0-6 for all days of the week
                num_days = random.randint(3, 5)
                if num_days > len(available_days):
                    num_days = len(available_days)
                
                selected_days = random.sample(available_days, num_days)
                
                for day in selected_days:
                    try:
                        schedule = DoctorSchedules.objects.create(
                            doctor=doctor,
                            hospital=hospital,
                            day=day
                        )
                        create_doctor_shifts(schedule, hospital)
                    except django_db_utils.IntegrityError:
                        print(f"Schedule already exists for doctor {doctor.full_name} on day {day}")
                        continue
            
            # Create pricing for each hospital
            create_doctor_pricing(doctor)
        
        doctors.append(doctor)
    return doctors

def create_doctor_shifts(schedule, hospital):
    shift_times = [
        (time(9, 0), time(12, 0)),
        (time(13, 0), time(16, 0)),
        (time(17, 0), time(20, 0))
    ]
    
    for start_time, end_time in random.sample(shift_times, random.randint(1, 3)):
        DoctorShifts.objects.create(
            doctor_schedule=schedule,
            hospital=hospital,
            start_time=start_time,
            end_time=end_time,
            available_slots=random.randint(5, 15),
            booked_slots=0
        )

def create_doctor_pricing(doctor):
    print(f"Creating pricing for doctor {doctor.full_name}...")
    for hospital in doctor.hospitals.all():
        DoctorPricing.objects.get_or_create(
            doctor=doctor,
            hospital=hospital,
            defaults={'amount': random.randint(100, 500)}
        )

def clear_existing_data():
    print("Clearing existing data...")
    DoctorShifts.objects.all().delete()
    DoctorSchedules.objects.all().delete()
    DoctorPricing.objects.all().delete()
    Doctor.objects.all().delete()
    Specialty.objects.all().delete()
    Hospital.objects.all().delete()
    CustomUser.objects.filter(user_type__in=['hospital_manager', 'admin']).delete()
    City.objects.all().delete()

def main():
    print("Starting to populate database...")
    clear_existing_data()
    cities = create_cities()
    admin_user = create_admin_user()
    hospital_users = create_hospital_users()
    hospitals = create_hospitals(hospital_users)
    specialties = create_specialties()
    doctors = create_doctors(specialties, hospitals)
    print("Database population completed!")

if __name__ == '__main__':
    main()
