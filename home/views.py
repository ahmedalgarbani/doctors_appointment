from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime
from home.helpers import group_shifts_by_period
from patients.models import Favourites, Patients
from .models import *
from doctors.models import Specialty, Doctor, DoctorPricing, DoctorSchedules,DoctorShifts
from hospitals.models import City, Hospital
from reviews.models import Review
from blog.models import Post
from datetime import datetime
from datetime import timedelta
from django.db.models import Min, Max, Avg, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
from django.contrib.auth.hashers import make_password,check_password

logger = logging.getLogger(__name__)

# Create your views here.

def index(request):

    try:
        homeBanner = HomeBanner.objects.first()
        logger.info('Retrieved home banner')
    except Exception as e:
        logger.error(f'Failed to retrieve home banner: {str(e)}')

    try:
        specialities = Specialty.objects.filter(show_at_home=True)
        logger.info('Retrieved specialities')
    except Exception as e:
        logger.error(f'Failed to retrieve specialities: {str(e)}')

    try:
        doctors = Doctor.objects.filter(show_at_home=True, status=True).select_related('specialty')
        logger.info('Retrieved doctors')
    except Exception as e:
        logger.error(f'Failed to retrieve doctors: {str(e)}')

    try:
        workSection = WorkSection.objects.first()
        logger.info('Retrieved work section')
    except Exception as e:
        logger.error(f'Failed to retrieve work section: {str(e)}')

    try:
        appSection = AppSection.objects.first()
        logger.info('Retrieved app section')
    except Exception as e:
        logger.error(f'Failed to retrieve app section: {str(e)}')

    try:
        faqSection = FAQSection.objects.first()
        logger.info('Retrieved faq section')
    except Exception as e:
        logger.error(f'Failed to retrieve faq section: {str(e)}')

    try:
        testimonialSection = TestimonialSection.objects.first()
        logger.info('Retrieved testimonial section')
    except Exception as e:
        logger.error(f'Failed to retrieve testimonial section: {str(e)}')

    try:
        partnersSection = PartnersSection.objects.filter(show_at_home=True)
        logger.info('Retrieved partners section')
    except Exception as e:
        logger.error(f'Failed to retrieve partners section: {str(e)}')

    try:
        socialMediaLinks = SocialMediaLink.objects.filter(status=True)
        logger.info('Retrieved socialmedia section')
    except Exception as e:
        logger.error(f'Failed to retrieve socialmedia section: {str(e)}')

    try:
        posts = Post.objects.filter(status=True)
        logger.info('Retrieved latest article section')
    except Exception as e:
        logger.error(f'Failed to retrieve latest article section: {str(e)}')

    try:
        setting = Setting.objects.first()
        logger.info('Retrieved latest setting section')
    except Exception as e:
        logger.error(f'Failed to retrieve setting article section: {str(e)}')

    try:
        cities = City.objects.filter(status=True)
        logger.info('Retrieved latest city section')
    except Exception as e:
        logger.error(f'Failed to retrieve city article section: {str(e)}')

    try:
        # الحصول على المستشفيات التي يجب عرضها في الصفحة الرئيسية
        hospitals = Hospital.objects.filter(show_at_home=True, status=True).select_related('city')

        # طباعة معلومات تصحيح
        logger.info(f'Found {hospitals.count()} hospitals for home page')
        for h in hospitals:
            logger.info(f'Hospital: {h.name}, City: {h.city.name if h.city else "No city"}, Status: {h.status}, Show at home: {h.show_at_home}')

        # إضافة عدد التخصصات وعدد جداول الأطباء لكل مستشفى
        for hospital in hospitals:
            hospital.specialties_count = hospital.doctors.values('specialty').distinct().count()
            hospital.schedules_count = DoctorSchedules.objects.filter(hospital=hospital).count()
            logger.info(f'Hospital {hospital.name}: {hospital.specialties_count} specialties, {hospital.schedules_count} schedules')

        logger.info('Retrieved hospitals for home page')
    except Exception as e:
        logger.error(f'Failed to retrieve hospitals: {str(e)}')
        hospitals = []

    # التأكد من أن المستشفيات موجودة
    if 'hospitals' not in locals() or hospitals is None:
        hospitals = []
        logger.warning('Hospitals variable not defined or is None, setting to empty list')

    # طباعة معلومات تصحيح
    logger.info(f'Context hospitals count: {len(hospitals)}')

    ctx = {
        'homeBanner': homeBanner,
        'specialities': specialities,
        'doctors': doctors,
        'workSection': workSection,
        'appSection': appSection,
        'faqSection': faqSection,
        'testimonialSection': testimonialSection,
        'partnersSection': partnersSection,
        'socialMediaLinks': socialMediaLinks,
        'posts': posts,
        'setting': setting,
        'cities': cities
    }
    logger.info('Context created successfully')
    return render(request, 'frontend/home/index.html', ctx)

def faq_page(request):
    faqs = FAQSection.objects.first()

    ctx = {
        'faqs': faqs
    }
    return render(request, 'frontend/home/pages/faq.html', ctx)

def privacy_policy(request):
    privacyPolicy = PrivacyPolicy.objects.first()

    ctx = {
        'privacyPolicy': privacyPolicy
    }
    return render(request, 'frontend/home/pages/privacy-policy.html', ctx)

def terms_condition(request):
    termsCondition = TermsConditions.objects.first()

    ctx = {
        'termsCondition': termsCondition
    }
    return render(request, 'frontend/home/pages/term-condition.html', ctx)


from math import floor
def doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.prefetch_related('hospitals', 'pricing'), id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor, status=True)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    average_rating =  int(floor(average_rating))
    doctor_prices = doctor.pricing.all().select_related('hospital')
    if request.method == 'POST':
         Review.objects.create(
            doctor_id = doctor_id,
            user = get_object_or_404(Patients,id=1),
            rating = request.POST.get('rating'),
            review = request.POST.get('review'),
            )
    day_date = datetime.now()
    day_name = day_date.strftime("%A")
    day_date = day_date.strftime("%Y-%m-%d")
    patient = get_object_or_404(Patients,id=1)
    isFavorite = patient.favourites.filter(doctor=doctor)

    ctx = {
        'doctor': doctor,
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
        'doctor_prices': doctor_prices,
        'day_name':day_name,
        'hospitals': doctor.hospitals.all(),
        'day_date':day_date,
        'isFavorite':isFavorite
    }

    return render(request, 'frontend/home/pages/doctor_profile.html', ctx)

import json

def add_to_favorites(request):
    try:
        data = json.loads(request.body)
        doctor_id = data.get('doctor_id')

        if not doctor_id:
            return JsonResponse({'status': 'error', 'message': 'No doctor ID provided'})

        doctor = get_object_or_404(Doctor, id=doctor_id)

        favorite_entry = Favourites.objects.filter(patient=get_object_or_404(Patients,id=1), doctor=doctor).first()

        if favorite_entry:
            favorite_entry.delete()
            return JsonResponse({'status': 'success', 'message': 'Doctor removed from favorites'})
        else:
            Favourites.objects.create(patient=get_object_or_404(Patients,id=1), doctor=doctor)
            return JsonResponse({'status': 'success', 'message': 'Doctor added to favorites'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def search_view(request):
    doctor_name = request.GET.get('doctor_name', '').strip()
    city_slug = request.GET.get('city', '').strip()
    gender = request.GET.get('gender')
    availability = request.GET.get('availability')
    fee_range = request.GET.get('fee_range')
    experience = request.GET.get('experience')
    rating = request.GET.get('rating')
    specialty = request.GET.get('specialty')
    page = request.GET.get('page', 1)

    filters = {}
    logger.info(f"Received filters - gender: {gender}, fee_range: {fee_range}, rating: {rating}, specialty: {specialty}, page: {page}")

    # قائمة الأطباء الأساسية
    doctors = Doctor.objects.all()

    if doctor_name:
        filters['full_name__icontains'] = doctor_name

    if city_slug:
        filters['hospitals__city__slug__in'] = [city_slug]

    if specialty:
        filters['specialty_id'] = specialty

    if gender:
        gender_map = {
            'male': 1,    # Doctor.STATUS_MALE
            'female': 0   # Doctor.STATUS_FAMEL
        }
        gender_value = gender_map.get(gender.lower())
        logger.info(f"Mapped gender value: {gender_value}")
        if gender_value is not None:
            filters['gender'] = gender_value

    # تطبيق فلتر نطاق السعر
    if fee_range:
        fee_ranges = {
            'low': (0, 100),
            'medium': (101, 200),
            'high': (201, 500),
            'very_high': (501, 999999)
        }
        if fee_range in fee_ranges:
            min_fee, max_fee = fee_ranges[fee_range]
            # الحصول على معرفات الأطباء الذين لديهم أسعار في النطاق المحدد
            doctor_ids = DoctorPricing.objects.filter(
                amount__gte=min_fee,
                amount__lte=max_fee
            ).values_list('doctor_id', flat=True).distinct()
            doctors = doctors.filter(id__in=doctor_ids)

    # تطبيق فلتر التقييم
    if rating:
        rating_value = float(rating)
        # احصل على معرفات الأطباء الذين لديهم متوسط تقييم أعلى من أو يساوي القيمة المحددة
        doctor_ids = Review.objects.filter(
            doctor__isnull=False,
            status=True  # فقط المراجعات النشطة
        ).values('doctor').annotate(
            avg_rating=Avg('rating')
        ).filter(
            avg_rating__gte=rating_value
        ).values_list('doctor', flat=True)

        doctors = doctors.filter(id__in=doctor_ids)

    # تطبيق فلتر الخبرة
    if experience:
        experience_ranges = {
            '0-2': (0, 2),
            '2-5': (2, 5),
            '5-10': (5, 10),
            '10+': (10, 999)
        }
        if experience in experience_ranges:
            min_exp, max_exp = experience_ranges[experience]
            doctors = doctors.filter(experience_years__gte=min_exp, experience_years__lte=max_exp)

    # تطبيق الفلاتر الأساسية
    doctors = doctors.filter(**filters).distinct()

    # تطبيق الترقيم
    paginator = Paginator(doctors, 10)  # 10 أطباء في كل صفحة
    try:
        doctors_page = paginator.page(page)
    except PageNotAnInteger:
        doctors_page = paginator.page(1)
    except EmptyPage:
        doctors_page = paginator.page(paginator.num_pages)

    cities = City.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'frontend/home/components/doctors_list.html', {
            'doctors': doctors_page,
            'page_obj': doctors_page,
        })

    # احصل على الحد الأدنى والأقصى للأسعار لعرضها في الواجهة
    price_range = DoctorPricing.objects.aggregate(
        min_price=Min('amount'),
        max_price=Max('amount')
    )

    # احصل على متوسط التقييمات لكل طبيب
    doctor_ratings = Review.objects.filter(
        doctor__in=doctors_page,
        status=True
    ).values('doctor').annotate(
        avg_rating=Avg('rating')
    )
    doctors_with_ratings = Doctor.objects.annotate(
        avg_rating=Avg('reviews__rating')
    )
    ctx = {
        'doctors': doctors_page,
        'page_obj': doctors_page,
        'cities': cities,
        'specialities': Specialty.objects.all(),
        'selected_filters': {
            'doctor_name': doctor_name,
            'city': city_slug,
            'gender': gender,
            'fee_range': fee_range,
            'experience': experience,
            'rating': rating,
            'specialty': specialty
        },
        'price_range': price_range,
        'doctors_with_ratings':doctors_with_ratings,
        'doctor_ratings': {r['doctor']: r['avg_rating'] for r in doctor_ratings}
    }

    return render(request, 'frontend/home/pages/search.html', ctx)






def booking_view(request, doctor_id):
    selected_doctor = get_object_or_404(Doctor, id=doctor_id)
    request.session['selected_doctor'] = selected_doctor.id

    # Get hospital_id from query parameters
    hospital_id = request.GET.get('hospital_id')

    # If no hospital is selected, use the first hospital
    if not hospital_id and selected_doctor.hospitals.exists():
        hospital_id = str(selected_doctor.hospitals.first().id)

    # Filter schedules by hospital
    if hospital_id:
        dayes = selected_doctor.schedules.filter(hospital_id=hospital_id)
        # Get doctor's price for selected hospital
        doctor_price = selected_doctor.pricing.filter(hospital_id=hospital_id).first()
    else:
        dayes = selected_doctor.schedules.all()
        doctor_price = None

    if dayes.exists():
        sched = dayes[0]
        schedulesShift = sched.shifts.all()
        grouped_slots = group_shifts_by_period(schedulesShift)
    else:
        sched = None
        grouped_slots = []

    context = {
        'doctor': selected_doctor,
        'dayes': dayes,
        'schedules': grouped_slots,
        'selected_day': sched.id if sched else None,
        'selected_hospital_id': hospital_id,
        'doctor_price': doctor_price,
        'doctor_prices': selected_doctor.pricing.all(),
    }

    return render(request, 'frontend/home/pages/booking.html', context)



from django.template.loader import render_to_string
def get_time_slots(request,schedule_id,doctor_id,):
    if not schedule_id:
        return JsonResponse({'error': 'No schedule ID provided'}, status=400)

    try:
        doctor = get_object_or_404(Doctor, id=doctor_id)
        schedule = get_object_or_404(DoctorSchedules, id=schedule_id, doctor=doctor)

        schedulesShift = schedule.shifts.all()
        grouped_slots = group_shifts_by_period(schedulesShift)

        html = render_to_string('frontend/home/pages/time_slots.html', {
            'schedules': grouped_slots,
            'doctor': doctor,
            'selected_day':schedule_id
        })

        return JsonResponse({
            'html': html,
            'schedule_id': schedule_id
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


