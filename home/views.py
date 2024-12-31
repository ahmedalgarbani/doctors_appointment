from django.shortcuts import render, get_object_or_404
from datetime import datetime
from home.helpers import group_shifts_by_period
from  patients.models import Patients
from payments.models import ChoosePayment, Payment, PaymentMethod, PaymentStatus
from .models import *
from doctors.models import Specialty, Doctor, DoctorPricing, DoctorSchedules,DoctorShifts
from hospitals.models import City, Hospital
from reviews.models import Review
from blog.models import Post
from datetime import datetime
from datetime import timedelta
from django.db.models import Min, Max, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging


from django.shortcuts import render, get_object_or_404
from doctors.models import Doctor, DoctorPricing
from django.db.models import Avg
from reviews.models import Review
from django.template.loader import render_to_string
from django.http import JsonResponse
from bookings.models import Booking
logger = logging.getLogger(__name__)

# Create your views here.

def index(request):
    request.session.flush()

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

    ctx = {
        'homeBanner': homeBanner,
        'specialities': specialities,
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

def profile(request):
    doctors = Doctor.objects.filter(status=True)
    
    ctx = {
        'doctors': doctors,
    }

    return render(request, 'frontend/home/pages/profile.html', ctx)

def doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.prefetch_related('hospitals'), id=doctor_id)

    reviews = Review.objects.filter(doctor=doctor, status=True)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    pricing = DoctorPricing.objects.filter(doctor=doctor).first()

    ctx = {
        'doctor': doctor,
        'reviews': reviews,
        'average_rating': average_rating,
        'pricing': pricing,
        'hospitals': doctor.hospitals.all(),
    }

    return render(request, 'frontend/home/pages/doctor_profile.html', ctx)




def search_view(request):
    search_text = request.GET.get('search', '').strip()  
    city_slug = request.GET.get('city', '').strip()
    date_str = request.GET.get('date', '').strip()
    gender = request.GET.get('gender')
    availability = request.GET.get('availability')
    fee_range = request.GET.get('fee_range')
    experience = request.GET.get('experience')
    rating = request.GET.get('rating')
    page = request.GET.get('page', 1)
    
    filters = {}
    logger.info(f"Received filters - gender: {gender}, fee_range: {fee_range}, rating: {rating}, page: {page}")

    # قائمة الأطباء الأساسية
    doctors = Doctor.objects.all()

    if search_text:
        filters['full_name__icontains'] = search_text
        filters['hospitals__name__icontains'] = search_text 

    if city_slug:
        city = City.objects.filter(slug=city_slug).first() 
        if city:
            filters['hospitals__city'] = city

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

    # تطبيق باقي الفلاتر
    if date_str:
        try:
            available_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            doctors = doctors.filter(schedules__day=available_date.strftime('%A'))
        except ValueError:
            pass

    if availability == 'today':
        today = datetime.now().strftime('%A')
        doctors = doctors.filter(schedules__day=today)
    elif availability == 'tomorrow':
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A')
        doctors = doctors.filter(schedules__day=tomorrow)

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
    ctx = {
        'doctors': doctors_page,
        'page_obj': doctors_page,
        'cities': cities,
        'selected_filters': {
            'search': search_text,
            'city': city_slug,
            'date': date_str,
            'gender': gender,
            'availability': availability,
            'fee_range': fee_range,
            'experience': experience,
            'rating': rating
        },
        'price_range': price_range,
        'doctor_ratings': {r['doctor']: r['avg_rating'] for r in doctor_ratings}
    }

    return render(request, 'frontend/home/pages/search.html', ctx)






def booking_view(request, doctor_id):
    selected_doctor = get_object_or_404(Doctor, id=doctor_id)
    request.session['selected_doctor'] = selected_doctor.id    
    dayes = selected_doctor.schedules.all()  
    sched = dayes[0]  

    schedulesShift = sched.shifts.all()

    grouped_slots = group_shifts_by_period(schedulesShift)
  
    context = {
        'doctor': selected_doctor,
        'dayes': dayes,
        'schedules': grouped_slots,
        'selected_day':sched.id,


        
    }

    return render(request, 'frontend/home/pages/booking.html', context)


def profile(request):
    doctors = Doctor.objects.filter(status=True)
    
    ctx = {
        'doctors': doctors,
    }

    return render(request, 'frontend/home/pages/profile.html', ctx)







def get_time_slots(request,schedule_id,doctor_id,):
    request.session['selected_day'] = schedule_id    

    if not schedule_id:
        return JsonResponse({'error': 'No schedule ID provided'}, status=400)

    doctor = get_object_or_404(Doctor, id=request.session['selected_doctor'])
    
    schedule = get_object_or_404(DoctorSchedules, id=schedule_id, doctor=doctor)
    
    schedulesShift = schedule.shifts.all()
    dayes = doctor.schedules.all()  

    grouped_slots = group_shifts_by_period(schedulesShift)
    ctx = {
        'schedules': grouped_slots, 
        'dayes': dayes,
        'doctor': doctor,
        'selected_day':schedule_id
    }
    # html = render_to_string('frontend/home/pages/time_slots.html', {})
    
    return render(request,'frontend/home/pages/booking.html',ctx)



def payment_process(request):
    doctor_id = request.session.get('selected_doctor')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    selected_date = request.session.get('selected_date', 0)
    selected_time = request.session.get('selected_time', 0)

    if request.method == 'GET':
        selected_date = get_object_or_404(DoctorSchedules, id=request.GET.get('day'))
        selected_time = get_object_or_404(DoctorShifts, id=request.GET.get('date'))
        request.session['selected_date'] = selected_date.id
        request.session['selected_time'] = selected_time.id
    elif request.method == 'POST':
        selected_date = get_object_or_404(DoctorSchedules, id=request.POST.get('selected_date', 0))
        selected_time = get_object_or_404(DoctorShifts, id=request.POST.get('selected_time', 0))
        request.session['selected_date'] = selected_date.id
        request.session['selected_time'] = selected_time.id

    hospital = doctor.hospitals.first()
    payment_methods = ChoosePayment.objects.filter(status=True)

    pricing = DoctorPricing.objects.filter(doctor=doctor, hospital=hospital).first()
    amount = pricing.amount if pricing else 0

    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        subtotal = float(request.POST.get('subtotal', 0)) if float(request.POST.get('subtotal', 0)) > 0 else float(amount)
        discount = float(request.POST.get('discount', 0))
        total = subtotal - discount
        transfer_number = request.POST.get('transfer_number', None)
        payment_method = request.POST.get('payment', 'cash')
     
        booking = Booking.objects.create(
            doctor=doctor,
            patient=get_object_or_404(Patients, id=1),
            hospital=get_object_or_404(Hospital, id=hospital.id),
            appointment_date=get_object_or_404(DoctorSchedules, id=selected_date.id),
            appointment_time=get_object_or_404(DoctorShifts, id=selected_time.id),
            notes=notes,
            amount=total,
            status='pending'
        )
       


        Payment.objects.create(
            booking=booking,
            payment_choose=get_object_or_404(ChoosePayment,id=payment_method),
            payment_status=get_object_or_404(PaymentStatus, id=1),
            payment_subtotal=subtotal,
            payment_discount=discount,
            payment_totalamount=total,
            payment_currency='RYL',
            payment_note=f"Transfer number: {transfer_number}",
            payment_type=get_object_or_404(PaymentMethod, id=payment_method).method_name
        )

        context = {
            'doctor': doctor,
            'hospital': hospital,
            'selected_date': selected_date.get_day_display,
            'selected_time': selected_time,
            'subtotal': subtotal,
            'discount': discount,
            'total': total,
            'transfer_number': transfer_number,
            'payment_method': payment_method,
        }
        return render(request, 'frontend/home/pages/booking-success.html', context)

    context = {
        'doctor': doctor,
        'hospital': hospital,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'amount': amount,
        'payment_methods': payment_methods,
    }
    return render(request, 'frontend/home/pages/payment.html', context)
