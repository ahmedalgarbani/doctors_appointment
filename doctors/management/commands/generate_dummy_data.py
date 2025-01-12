from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from doctors.models import Specialty, Doctor, DoctorSchedules, DoctorShifts, DoctorPricing
from hospitals.models import City, Hospital
from payments.models import PaymentStatus, PaymentOption, HospitalPaymentMethod
from django.utils import timezone
from datetime import time, timedelta, date
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates dummy data for the doctors appointment system'

    def handle(self, *args, **kwargs):
        # Create superuser
        try:
            superuser = User.objects.create_superuser(
                username='ali',
                email='ali@example.com',
                password='123'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created superuser'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Superuser already exists: {e}'))

        # Create Payment Statuses
        payment_statuses = [
            {"name": "معلق", "code": 1},
            {"name": "مكتمل", "code": 2},
            {"name": "ملغي", "code": 3},
            {"name": "مرفوض", "code": 4},
            {"name": "قيد المعالجة", "code": 5},
        ]
        
        for status in payment_statuses:
            payment_status, created = PaymentStatus.objects.get_or_create(
                payment_status_name=status["name"],
                defaults={'status_code': status["code"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created payment status: {status["name"]}'))

        # Create Payment Options
        payment_options = [
            {"name": "مدى", "currency": "SAR"},
            {"name": "فيزا", "currency": "SAR"},
            {"name": "ماستر كارد", "currency": "SAR"},
            {"name": "Apple Pay", "currency": "SAR"},
            {"name": "نقدي", "currency": "SAR"},
        ]
        
        payment_option_objects = []
        for option in payment_options:
            payment_option, created = PaymentOption.objects.get_or_create(
                method_name=option["name"],
                defaults={
                    'currency': option["currency"],
                    'is_active': True
                }
            )
            payment_option_objects.append(payment_option)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created payment option: {option["name"]}'))

        # Create specialties
        specialties = [
            "طب الأسنان",
            "طب العيون",
            "طب الأطفال",
            "طب القلب",
            "طب العظام",
        ]
        
        specialty_objects = []
        for specialty_name in specialties:
            specialty, created = Specialty.objects.get_or_create(
                name=specialty_name,
                defaults={'created_by': superuser}
            )
            specialty_objects.append(specialty)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created specialty: {specialty_name}'))

        # Create cities
        cities = ["الرياض", "جدة", "الدمام", "مكة", "المدينة"]
        city_objects = []
        for city_name in cities:
            city, created = City.objects.get_or_create(
                name=city_name,
                defaults={'slug': city_name}
            )
            city_objects.append(city)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created city: {city_name}'))

        # Create hospitals
        hospitals = [
            "مستشفى الملك فهد",
            "مستشفى الملك فيصل",
            "مستشفى الملك خالد",
            "مستشفى الملك سعود",
            "المستشفى السعودي الألماني",
        ]
        
        hospital_objects = []
        for i, hospital_name in enumerate(hospitals):
            hospital, created = Hospital.objects.get_or_create(
                name=hospital_name,
                defaults={
                    'location': f'موقع {hospital_name}',
                    'slug': hospital_name.replace(" ", "-"),
                    'city': random.choice(city_objects),
                    'created_by': superuser
                }
            )
            hospital_objects.append(hospital)
            if created:
                # Create hospital details
                # HospitalDetail.objects.create(
                #     hospital=hospital,
                #     description=f'وصف {hospital_name}',
                #     specialty=random.choice(specialty_objects),
                #     sub_title=f'عنوان فرعي ل{hospital_name}',
                #     about=f'معلومات عن {hospital_name}',
                #     created_by=superuser
                # )
                
                # Create Hospital Payment Methods
                for payment_option in payment_option_objects:
                    HospitalPaymentMethod.objects.create(
                        hospital=hospital,
                        payment_option=payment_option,
                        account_name=f"حساب {hospital_name}",
                        account_number=f"{random.randint(1000000000, 9999999999)}",
                        iban=f"SA{random.randint(100000000000000000000000, 999999999999999999999999)}",
                        description=f"تعليمات الدفع ل{payment_option.method_name} في {hospital_name}",
                        is_active=True
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Created hospital: {hospital_name}'))

        # Create doctors
        doctor_names = [
            "د. أحمد محمد",
            "د. محمد علي",
            "د. فاطمة أحمد",
            "د. سارة خالد",
            "د. عبدالله محمد",
        ]

        for i, doctor_name in enumerate(doctor_names):
            doctor, created = Doctor.objects.get_or_create(
                full_name=doctor_name,
                defaults={
                    'birthday': date(1980 + i, 1, 1),
                    'phone_number': f'05{random.randint(10000000, 99999999)}',
                    'specialty': random.choice(specialty_objects),
                    'gender': random.choice([0, 1]),
                    'email': f'doctor{i+1}@example.com',
                    'experience_years': random.randint(5, 20),
                    'sub_title': f'أخصائي {random.choice(specialties)}',
                    'about': f'نبذة عن {doctor_name}',
                    'created_by': superuser
                }
            )
            
            if created:
                # Add hospitals to doctor
                doctor.hospitals.add(*random.sample(hospital_objects, random.randint(1, 3)))
                
                # Create doctor schedules
                for day in range(7):  # 0 = Saturday to 6 = Friday
                    if random.choice([True, False]):  # Randomly decide if doctor works this day
                        schedule = DoctorSchedules.objects.create(
                            doctor=doctor,
                            hospital=random.choice(doctor.hospitals.all()),
                            day=day
                        )
                        
                        # Create shifts for this schedule
                        start_hours = [9, 14, 17]  # Morning, afternoon, and evening shifts
                        for hour in start_hours:
                            if random.choice([True, False]):
                                DoctorShifts.objects.create(
                                    doctor_schedule=schedule,
                                    start_time=time(hour, 0),
                                    end_time=time(hour + 3, 0),
                                    available_slots=random.randint(5, 15),
                                    booked_slots=0
                                )
                
                # Create doctor pricing
                for hospital in doctor.hospitals.all():
                    DoctorPricing.objects.create(
                        doctor=doctor,
                        hospital=hospital,
                        amount=random.randint(200, 500)
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Created doctor: {doctor_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully generated all dummy data'))
