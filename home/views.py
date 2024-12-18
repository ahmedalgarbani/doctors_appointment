from django.shortcuts import render
from .models import *
from doctors.models import Specialty,Doctor
from hospitals.models import City
import logging
from django.shortcuts import render
from blog.models import Post
from datetime import datetime

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
        logger.info('Retrieved latest artichal section')
    except Exception as e:
        logger.error(f'Failed to retrieve latest artichal section: {str(e)}')

    try:
        setting = Setting.objects.first()
        logger.info('Retrieved latest setting section')
    except Exception as e:
        logger.error(f'Failed to retrieve setting artichal section: {str(e)}')

    try:
        cities = City.objects.filter(status = True)
        logger.info('Retrieved latest city section')
      
    except Exception as e:
        logger.error(f'Failed to retrieve city artichal section: {str(e)}')

    ctx = {
        'homeBanner':homeBanner,
        'specialities':specialities,
        'workSection':workSection,
        'appSection':appSection,
        'faqSection':faqSection,
        'testimonialSection':testimonialSection,
        'partnersSection':partnersSection,
        'socialMediaLinks':socialMediaLinks,
        'posts':posts,
        'setting':setting,
        'cities':cities
    }
    logger.info('Context created successfully')
    return render(request,'frontend/home/index.html',ctx)


def faq_page(request):
    faqs = FAQSection.objects.first()

    ctx = {
        'faqs':faqs
    }
    return render(request,'frontend/home/pages/faq.html',ctx)
def privacy_policy(request):
    privacyPolicy = PrivacyPolicy.objects.first()

    ctx = {
        'privacyPolicy':privacyPolicy
    }
    return render(request,'frontend/home/pages/privacy-policy.html',ctx)


def terms_condition(request):
    termsCondition = TermsConditions.objects.first()

    ctx = {
        'termsCondition':termsCondition
    }
    return render(request,'frontend/home/pages/term-condition.html',ctx)




def search_view(request):
    search_text = request.GET.get('search', '').strip()  
    city_slug = request.GET.get('city', '').strip()
    date_str = request.GET.get('date', '').strip()

    filters = {}

    if search_text:
        filters['full_name__icontains'] = search_text
        filters['hospitals__name__icontains'] = search_text 

    if city_slug:
        city = City.objects.filter(slug=city_slug).first() 
        if city:
            filters['hospitals__city'] = city

    if date_str:
        try:
            available_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            filters['schedules__day'] = available_date.strftime('%A') 
        except ValueError:
            filters['available_date'] = None

    doctors = Doctor.objects.filter(**filters).distinct()

    cities = City.objects.all()

    ctx = {
        'doctors': doctors,
        'cities': cities,
    }


    return render(request, 'frontend/home/pages/search.html', ctx)


