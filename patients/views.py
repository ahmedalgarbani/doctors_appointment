from django.shortcuts import render, get_object_or_404, redirect
from .models import Patients, Favourites
from bookings.models import Booking
from doctors.models import Doctor, DoctorSchedules, DoctorShifts
from reviews.models import Review
from notifications.models import Notifications
from django.db.models import Avg, Prefetch ,Sum
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
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import logging

@login_required(login_url='/user/login')
def patient_dashboard(request):
    user = request.user
    patient = get_object_or_404(Patients, user_id=user)

    # التحقق إذا تم إرسال تحديث للملف الشخصي
    if request.method == 'POST' and 'update_profile' in request.POST:
        return update_patient_profile(request, patient)
    
    # حذف إشعارات إذا تم تحديد ذلك
    if request.method == 'POST' and 'notification_id' in request.body.decode('utf-8'):
        import json
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        result = delete_notification(notification_id, user)
        return JsonResponse(result)

    # جلب الأطباء المفضلين والتقييمات
    favourite_doctors, ratings_context = get_favourites_and_ratings(patient)
    for doctor in favourite_doctors:
        average_rating = doctor.reviews.aggregate(Avg('rating'))['rating__avg']
        doctor.average_rating = average_rating if average_rating is not None else 0

    # عدد الحجوزات
    bookings_count = Booking.objects.filter(patient=patient).count()

    # جلب المدفوعات الخاصة بالمريض
    payments = Payment.objects.select_related('booking__doctor').filter(booking__patient=patient)

    # حساب مجموع المدفوعات المكتملة
    total_paid = payments.filter(payment_status=1).aggregate(
        total=Sum('payment_totalamount')
    )['total'] or 0

    # تحديد العملة (إذا لا توجد دفعات، تعيين عملة افتراضية)
    currency = payments.filter(payment_status=1).first().payment_currency if total_paid > 0 else 'RYL'

    context = {
        'patient': patient,
        'user': patient.user,
        'favourites': Favourites.objects.filter(patient=patient),
        'bookings': Booking.objects.filter(patient=patient),
        'favourite_doctors': favourite_doctors,
        'ratings_context': ratings_context,
        'bookings_count': bookings_count,
        'payments': payments,
        'total_paid': total_paid,
        'currency': currency,
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
    user = patient.user
    user.first_name = request.POST.get('first_name')
    user.last_name = request.POST.get('last_name')
    user.email = request.POST.get('email')
    user.mobile_number = request.POST.get('mobile_number')
    user.address = request.POST.get('address')
    user.city = request.POST.get('city')
    user.state = request.POST.get('state')

    if request.FILES.get('profile_picture'):
        user.profile_picture = request.FILES['profile_picture']
    user.save()

    patient.birth_date = request.POST.get('birth_date') or None
    patient.gender = request.POST.get('gender') or None

    weight = request.POST.get('weight')
    patient.weight = float(weight) if weight and weight.lower() != 'none' else None

    height = request.POST.get('height')
    patient.height = float(height) if height and height.lower() != 'none' else None

    age = request.POST.get('age')
    patient.age = int(age) if age and age.lower() != 'none' else None

    patient.blood_group = request.POST.get('blood_group') or None
    patient.notes = request.POST.get('notes') or ''

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


def appointment_details(request, booking_id):
    """عرض تفاصيل الحجز في صفحة منفصلة"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    context = {
        'booking': booking,
        'page_title': 'تفاصيل الحجز'
    }
    
    return render(request, 'frontend/dashboard/patient/sections/appointment_details.html', context)



logger = logging.getLogger(__name__)

@require_POST
@login_required
def cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # التحقق من ملكية الحجز
        if booking.patient.user != request.user:
            logger.warning(f"User {request.user.id} tried to cancel booking {booking_id} they don't own")
            raise PermissionDenied("ليس لديك صلاحية لإلغاء هذا الحجز")
        
        # التحقق من حالة الحجز
        if booking.status not in ['pending', 'confirmed']:
            return JsonResponse({
                'success': False,
                'message': 'لا يمكن إلغاء الحجز في حالته الحالية'
            }, status=400)
        
        # إلغاء الحجز
        booking.status = 'cancelled'
        booking.cancellation_reason = 'تم الإلغاء من قبل المريض'
        booking.save()
        
        # هنا يمكنك إضافة إرسال إشعار للطبيب أو أي إجراءات أخرى
        
        logger.info(f"Booking {booking_id} cancelled successfully by user {request.user.id}")
        return JsonResponse({
            'success': True, 
            'message': 'تم إلغاء الحجز بنجاح',
            'new_status': 'cancelled',
            'status_display': booking.get_status_display()
        })
        
    except PermissionDenied as e:
        return JsonResponse({
            'success': False, 
            'message': str(e)
        }, status=403)
        
    except Exception as e:
        logger.error(f"Error cancelling booking {booking_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'حدث خطأ غير متوقع أثناء معالجة الطلب'
        }, status=500)
    
from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookingForm
from bookings.models import Booking, DoctorSchedules, DoctorShifts, HospitalPaymentMethod

def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # الحصول على اختيارات اليوم (DoctorSchedules) للمستشفى
    doctor_schedules = DoctorSchedules.objects.filter(
        doctor=booking.doctor,  # تصفية حسب الطبيب
        hospital=booking.hospital  # تصفية حسب المستشفى
    )

    # الحصول على الأوقات المتاحة (DoctorShifts) بناءً على المواعيد المحجوزة
    doctor_shifts = DoctorShifts.objects.filter(
        doctor_schedule__in=doctor_schedules
    )

    # اليوم المفضل عند تحميل الصفحة
    selected_day = booking.appointment_date.day if booking.appointment_date else None

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()  # حفظ التعديلات
            return redirect('patients:patient_dashboard')
    else:
        form = BookingForm(instance=booking)

    # الحصول على اختيارات اليوم والوقت وطريقة الدفع
    days_choices = doctor_schedules
    times = doctor_shifts.filter(doctor_schedule__day=selected_day) if selected_day else doctor_shifts
    payment_methods = HospitalPaymentMethod.objects.all()

    context = {
        'form': form,
        'booking': booking,
        'days_choices': days_choices,
        'times': times,
        'payment_methods': payment_methods
    }

    return render(request, 'frontend/dashboard/patient/sections/edit_booking.html', context)
