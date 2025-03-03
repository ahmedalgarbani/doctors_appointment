from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from doctors.models import Specialty, Doctor, DoctorSchedules, DoctorShifts, DoctorPricing
from hospitals.models import City, Hospital
from users.models import CustomUser
import random
from datetime import time, timedelta, datetime

fake = Faker(['ar_SA', 'ar_EG'])

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create Cities
        cities = self.create_cities()
        
        # Create Users and Hospitals
        admin_user = self.create_admin_user()
        hospital_users = self.create_hospital_users()
        hospitals = self.create_hospitals(hospital_users)
        
        # Create Specialties
        specialties = self.create_specialties()
        
        # Create Doctors and related data
        doctors = self.create_doctors(specialties, hospitals)
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))

    def create_cities(self):
        cities = []
        city_names = ['الرياض', 'جدة', 'الدمام', 'مكة المكرمة', 'المدينة المنورة']
        
        for name in city_names:
            city, created = City.objects.get_or_create(
                name=name,
                slug=name.replace(' ', '-'),
                status=True
            )
            cities.append(city)
        
        return cities

    def create_admin_user(self):
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

    def create_hospital_users(self):
        users = []
        for i in range(5):
            user = CustomUser.objects.create(
                username=f'hospital_manager_{i}',
                email=f'hospital{i}@example.com',
                user_type='hospital_manager',
                mobile_number=f'05{str(random.randint(10000000, 99999999))}',
                address=fake.address(),
                city=fake.city(),
                state=fake.state(),
            )
            user.set_password('hospital123')
            user.save()
            users.append(user)
        return users

    def create_hospitals(self, hospital_users):
        hospitals = []
        for user in hospital_users:
            hospital = Hospital.objects.create(
                user=user,
                name=fake.company(),
                slug=fake.slug(),
                description=fake.text(),
                sub_title=fake.catch_phrase(),
                about=fake.paragraph(),
                status=True,
                show_at_home=True,
                created_by=user
            )
            hospitals.append(hospital)
        return hospitals

    def create_specialties(self):
        specialties = []
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
        
        for name in specialty_names:
            specialty = Specialty.objects.create(
                name=name,
                show_at_home=True,
                status=True
            )
            specialties.append(specialty)
        
        return specialties

    def create_doctors(self, specialties, hospitals):
        doctors = []
        for i in range(20):
            doctor = Doctor.objects.create(
                full_name=fake.name(),
                birthday=fake.date_of_birth(minimum_age=30, maximum_age=70),
                phone_number=f'05{str(random.randint(10000000, 99999999))}',
                specialty=random.choice(specialties),
                gender=random.choice([0, 1]),
                email=fake.email(),
                experience_years=random.randint(1, 30),
                sub_title=fake.catch_phrase(),
                about=fake.paragraph(),
                status=True,
                show_at_home=random.choice([True, False])
            )
            
            # Add random hospitals to doctor
            doctor.hospitals.add(*random.sample(hospitals, random.randint(1, 3)))
            
            # Create doctor schedules
            self.create_doctor_schedules(doctor, hospitals)
            
            # Create doctor pricing
            self.create_doctor_pricing(doctor, hospitals)
            
            doctors.append(doctor)
        
        return doctors

    def create_doctor_schedules(self, doctor, hospitals):
        for hospital in doctor.hospitals.all():
            # Create schedules for random days
            days = random.sample(range(7), random.randint(3, 5))
            for day in days:
                schedule = DoctorSchedules.objects.create(
                    doctor=doctor,
                    hospital=hospital,
                    day=day
                )
                
                # Create shifts for each schedule
                self.create_doctor_shifts(schedule, hospital)

    def create_doctor_shifts(self, schedule, hospital):
        shift_start = time(9, 0)  # 9 AM
        for _ in range(random.randint(1, 3)):
            start_time = shift_start
            end_time = time(start_time.hour + 3, 0)  # 3-hour shifts
            
            DoctorShifts.objects.create(
                doctor_schedule=schedule,
                hospital=hospital,
                start_time=start_time,
                end_time=end_time,
                available_slots=random.randint(5, 15),
                booked_slots=0
            )
            
            shift_start = time(end_time.hour + 1, 0)  # 1-hour break between shifts

    def create_doctor_pricing(self, doctor, hospitals):
        for hospital in doctor.hospitals.all():
            DoctorPricing.objects.create(
                doctor=doctor,
                hospital=hospital,
                amount=random.randint(100, 500)
            )
