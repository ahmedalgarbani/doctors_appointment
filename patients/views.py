from django.shortcuts import render, get_object_or_404
from .models import Patients, Favourites
from bookings.models import Booking
from doctors.models import Doctor
from reviews.models import Review
from django.db.models import Avg, Prefetch
from datetime import datetime


def appointments_dashboard(request):
    patients = Patients.objects.all()
    favourites = Favourites.objects.filter(user=request.user) if request.user.is_authenticated else None

    context = {
        'patients': patients,
        'favourites': favourites,
    }
    return render(request, 'frontend/dashboard/doctor/index.html', context)


def patients_list(request):
    # جلب قائمة جميع المرضى
    patients = Patients.objects.all()
    context = {
        'patients': patients,
    }
    return render(request, 'frontend/dashboard/patient/sections/patient_lite.html', context)


def patient_dashboard(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)

    # جلب المفضلات والتقييمات
    favourite_doctors, ratings_context = get_favourites_and_ratings(patient)

    if request.method == 'POST':
        # استدعاء دالة تحديث بيانات المريض
        update_patient_data(patient, request)

    context = {
        'patient': patient,
        'favourites': Favourites.objects.filter(patient=patient),
        'bookings': Booking.objects.filter(patient=patient),
        'favourite_doctors': favourite_doctors,
        'ratings_context': ratings_context,
        
    }

    return render(request, 'frontend/dashboard/patient/index.html', context)


def update_patient_data(patient, request):
    """
    دالة لتحديث بيانات المريض.
    """
    patient.full_name = request.POST.get('full_name', patient.full_name)
    
    birth_date_str = request.POST.get('birth_date', '')
    if birth_date_str:
        try:
            patient.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            patient.birth_date = None 
    
    patient.gender = request.POST.get('gender', patient.gender)
    patient.email = request.POST.get('email', patient.email)
    patient.phone_number = request.POST.get('phone_number', patient.phone_number)
    patient.address = request.POST.get('address', patient.address)
    patient.notes = request.POST.get('notes', patient.notes)

    if request.FILES.get('profile_picture'):
        patient.profile_picture = request.FILES['profile_picture']

    # حفظ التغييرات
    patient.save()



def get_favourites_and_ratings(patient):
    favourites = Favourites.objects.filter(patient=patient)
    favourite_doctors = [favourite.doctor for favourite in favourites]
    
    # Get doctors with their reviews
    doctors_with_reviews = Doctor.objects.prefetch_related(
        Prefetch('reviews', queryset=Review.objects.all(), to_attr='doctor_reviews')
    ).filter(id__in=[doctor.id for doctor in favourite_doctors])
    
    # Calculate average ratings for each doctor
    ratings_context = {}
    for doctor in doctors_with_reviews:
        reviews = doctor.doctor_reviews
        if reviews:
            # Calculate average rating
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / len(reviews)
        else:
            average_rating = 0
        ratings_context[str(doctor.id)] = average_rating

    return favourite_doctors, ratings_context
