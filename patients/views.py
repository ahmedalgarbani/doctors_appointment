from django.shortcuts import render, get_object_or_404, redirect
from .models import Patients, Favourites
from bookings.models import Booking
from doctors.models import Doctor
from reviews.models import Review
from notifications.models import Notifications
from django.db.models import Avg, Prefetch 
from datetime import datetime
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import PatientProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from payments.models import (
    HospitalPaymentMethod,
    PaymentOption,
    Payment,
)

@login_required(login_url='/user/login')
def patient_dashboard(request):
    user = request.user
    patient = get_object_or_404(Patients, user_id=user)

    # التحقق إذا كان تم إرسال تحديث للملف الشخصي
    if request.method == 'POST' and 'update_profile' in request.POST:
        return update_patient_profile(request, patient)
    
    # حذف إشعارات إذا تم تحديد ذلك
    if request.method == 'POST' and 'notification_id' in request.body.decode('utf-8'):
        import json
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        result = delete_notification(notification_id, user)
        return JsonResponse(result)

    # الحصول على الإشعارات الخاصة بالمريض
    notifications = get_notifications_for_user(user_id=user)
    unread_notifications_count = notifications.filter(status='0').count()

    # الحصول على الأطباء المفضلين والتقييمات
    favourite_doctors, ratings_context = get_favourites_and_ratings(patient)
    for doctor in favourite_doctors:
        average_rating = doctor.reviews.aggregate(Avg('rating'))['rating__avg']
        doctor.average_rating = average_rating if average_rating is not None else 0

    bookings_count = Booking.objects.filter(patient=patient).count()

    # جلب المدفوعات الخاصة بالمريض
    payments = Payment.objects.select_related('booking__doctor').filter(booking__patient=patient)

    context = {
        'patient': patient,
        'user': patient.user,
        'favourites': Favourites.objects.filter(patient=patient),
        'bookings': Booking.objects.filter(patient=patient),
        'favourite_doctors': favourite_doctors,
        'ratings_context': ratings_context,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'bookings_count': bookings_count,
        'payments': payments, 
    }

    return render(request, 'frontend/dashboard/patient/index.html', context)



def get_favourites_and_ratings(patient):
    """
    دالة لجلب الأطباء المفضلين وحساب تقييماتهم.
    """
    favourites = Favourites.objects.filter(patient=patient)
    favourite_doctors = [favourite.doctor for favourite in favourites]
    
    doctors_with_reviews = Doctor.objects.prefetch_related(
        Prefetch('reviews', queryset=Review.objects.all(), to_attr='doctor_reviews')
    ).filter(id__in=[doctor.id for doctor in favourite_doctors])
    
    # حساب متوسط التقييمات لكل طبيب
    ratings_context = {}
    for doctor in doctors_with_reviews:
        reviews = doctor.doctor_reviews
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / len(reviews)
        else:
            average_rating = 0
        ratings_context[str(doctor.id)] = average_rating

    return favourite_doctors, ratings_context

def get_notifications_for_user(user_id):
    """
    دالة لجلب الإشعارات الخاصة بالمستخدم الذي يمتلك id معين.
    """
    notifications = Notifications.objects.filter(user_id=user_id, is_active=True).order_by('-send_time')
    return notifications

def delete_notification(notification_id, user):
    """
    دالة لحذف الإشعار بناءً على معرف الإشعار والمستخدم.
    """
    try:
        notification = Notifications.objects.get(id=notification_id, user=user, is_active=True)
        notification.delete()
        return {"success": True}
    except Notifications.DoesNotExist:
        return {"success": False, "error": "Notification not found."}


from django import forms
from django.contrib.auth.forms import PasswordChangeForm
def update_patient_profile(request, patient):
    # تحديث البيانات بناءً على الحقول المدخلة
    patient.user.first_name = request.POST.get('first_name')
    patient.user.last_name = request.POST.get('last_name')
    patient.user.email = request.POST.get('email')
    patient.user.mobile_number = request.POST.get('mobile_number')
    patient.user.address = request.POST.get('address')
    patient.user.city = request.POST.get('city')
    patient.user.state = request.POST.get('state')
    patient.birth_date = request.POST.get('birth_date')
    patient.gender = request.POST.get('gender')
    patient.weight = request.POST.get('weight')
    patient.height = request.POST.get('height')
    patient.age = request.POST.get('age')
    patient.blood_group = request.POST.get('blood_group')
    patient.notes = request.POST.get('notes')
    
    # تحديث الصورة الشخصية إذا تم رفع صورة جديدة
    if request.FILES.get('profile_picture'):
        patient.user.profile_picture = request.FILES['profile_picture']
    
    # حفظ البيانات بعد التعديل
    patient.user.save()
    patient.save()

    return redirect('patients:patient_dashboard')


def user_logout(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/user/login')
def invoice_view(request, payment_id):
    # الحصول على الفاتورة المحددة
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'frontend/dashboard/patient/sections/invoice_view.html', {'payment': payment})


import logging

logger = logging.getLogger(__name__)

def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        
        # التحقق من كلمة المرور القديمة
        if not request.user.check_password(old_password):
            messages.error(request, 'كلمة المرور القديمة غير صحيحة.')
            return redirect('patients:change_password')

        # التحقق من تطابق كلمة المرور الجديدة مع تأكيد كلمة المرور
        if new_password != request.POST.get('confirm_password'):
            messages.error(request, 'كلمة المرور الجديدة وتأكيد كلمة المرور لا يتطابقان.')
            return redirect('patients:change_password')

        # تحديث كلمة المرور الجديدة
        logger.info(f'Changing password for user {request.user.username}')
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        logger.info(f'Password successfully changed for user {request.user.username}')
        messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
        return redirect('patients:patient_dashboard')
