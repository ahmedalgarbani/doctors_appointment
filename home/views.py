from django.shortcuts import render
from .models import *
from doctors.models import Specialty
import logging
from blog.models import Post
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
        'setting':setting
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
