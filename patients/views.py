from django.shortcuts import render, get_object_or_404
from .models import Patients, Favourites
from bookings.models import Booking
from doctors.models import Doctor
from reviews.models import Review
from notifications.models import Notifications
from django.db.models import Avg, Prefetch
from datetime import datetime
from django.http import JsonResponse

def patient_dashboard(request):
    user_id = 1
    patient = get_object_or_404(Patients, user_id=user_id)

        # معالجة طلب الحذف إذا كان الطلب POST وفيه notification_id
    if request.method == 'POST' and 'notification_id' in request.body.decode('utf-8'):
        import json
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        result = delete_notification(notification_id, user_id)
        return JsonResponse(result)

    notifications = get_notifications_for_user(user_id=user_id)

    unread_notifications_count = notifications.filter(status='0').count()

    favourite_doctors, ratings_context = get_favourites_and_ratings(patient)
    for doctor in favourite_doctors:
        average_rating = doctor.reviews.aggregate(Avg('rating'))['rating__avg']
        doctor.average_rating = average_rating if average_rating is not None else 0

    if request.method == 'POST':
        update_patient_data(patient, request)

    context = {
        'patient': patient,
        'favourites': Favourites.objects.filter(patient=patient),
        'bookings': Booking.objects.filter(patient=patient),
        'favourite_doctors': favourite_doctors,
        'ratings_context': ratings_context,
        'notifications': notifications, 
        'unread_notifications_count': unread_notifications_count,  
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

    patient.save()

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
        # الحصول على الإشعار والتأكد من أنه مرتبط بالمستخدم
        notification = Notifications.objects.get(id=notification_id, user=user, is_active=True)
        notification.delete()
        return {"success": True}
    except Notifications.DoesNotExist:
        return {"success": False, "error": "Notification not found."}
