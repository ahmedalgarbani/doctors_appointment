from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor, DoctorPricing, DoctorSchedules, DoctorShifts
from hospitals.models import Hospital
from notifications.models import Notifications
from .models import HospitalPaymentMethod, Payment
from bookings.models import Booking
from django.http import HttpResponseBadRequest
from patients.models import Patients

# Create your views here.

def payment_process(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Verify required values
    if request.method == 'POST':
        day_id = request.POST.get('day')
        date_id = request.POST.get('date')
        booking_date = request.POST.get('booking_date')
        hospital_id = request.POST.get('hospital_id')
    else:
        day_id = request.GET.get('day')
        date_id = request.GET.get('date')
        booking_date = request.GET.get('booking_date')
        hospital_id = request.GET.get('hospital_id')

    print("Day ID:", day_id)
    print("Date ID:", date_id)
    print("Booking Date:", booking_date)
    print("Hospital ID:", hospital_id)

    if not all([day_id, date_id, booking_date, hospital_id]):
        return HttpResponseBadRequest('يرجى اختيار اليوم والوقت وتاريخ الحجز والمستشفى')

    try:
        # Get hospital and validate it's associated with the doctor
        selected_hospital = get_object_or_404(Hospital, id=hospital_id)
        if not doctor.hospitals.filter(id=hospital_id).exists():
            return HttpResponseBadRequest('المستشفى المختار غير مرتبط بالطبيب')

        # Get doctor's price for this hospital
        doctor_price = get_object_or_404(DoctorPricing, doctor=doctor, hospital=selected_hospital)
        
        # Validate schedule and shift IDs
        selected_schedule = get_object_or_404(DoctorSchedules, id=day_id, doctor=doctor)
        selected_shift = get_object_or_404(DoctorShifts, id=date_id, doctor_schedule=selected_schedule)

        # Check if the appointment is available
        if not selected_shift.is_available:
            return HttpResponseBadRequest('عذراً، هذا الموعد غير متاح')

    except (ValueError, TypeError):
        return HttpResponseBadRequest('معرف اليوم أو الوقت غير صالح')


    # Get payment methods
    payment_methods = HospitalPaymentMethod.objects.filter(hospital=selected_hospital, is_active=True)

    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        payment_type = request.POST.get('payment_type')
        notes = request.POST.get('notes', '')

        print("POST request received")
        print("Payment method:", payment_method_id)
        print("Payment type:", payment_type)

        if not payment_method_id:
            return HttpResponseBadRequest('يرجى اختيار طريقة الدفع')

        transfer_number = None
        account_image = None

        if payment_type == 'transfer':
            transfer_number = request.POST.get('transfer_number')
            if not transfer_number:
                return HttpResponseBadRequest('يرجى إدخال رقم الحوالة')
            if not transfer_number.isdigit() or len(transfer_number) < 5:
                return HttpResponseBadRequest('رقم الحوالة يجب أن يكون 5 أرقام على الأقل')
        else:  # payment_type == 'account'
            # صورة السند اختيارية
            if 'account_image' in request.FILES:
                account_image = request.FILES['account_image']

        try:
            payment_method = payment_methods.get(id=payment_method_id)
        except HospitalPaymentMethod.DoesNotExist:
            return HttpResponseBadRequest('طريقة الدفع غير صالحة')

        # Re-check appointment availability
        if not selected_shift.is_available:
            return HttpResponseBadRequest('عذراً، هذا الموعد لم يعد متاحاً')

        # Get the patient
        try:
            patient = Patients.objects.get(user=request.user)
        except Patients.DoesNotExist:
            return HttpResponseBadRequest('عذراً، لم يتم العثور على بيانات المريض')

        # Create the booking
        booking = Booking.objects.create(
            doctor=doctor,
            patient=patient,
            hospital=selected_hospital,
            appointment_date=selected_schedule,
            appointment_time=selected_shift,
            booking_date=booking_date,
            amount=doctor_price.amount,
            status='pending',
            transfer_number=transfer_number,
            payment_method=payment_method,
            account_image=account_image if payment_type == 'account' else None
        )

        # Create the payment
        subtotal = float(request.POST.get('subtotal', doctor_price.amount))
        discount = float(request.POST.get('discount', 0))
        total = subtotal - discount

        Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            payment_status=0,
            payment_subtotal=subtotal,
            payment_discount=discount,
            payment_totalamount=total,
            payment_currency=payment_method.payment_option.currency,
            payment_note=notes,
        )

        # إرسال إشعار للمستشفى بوجود حجز جديد
        from notifications.models import Notifications

        # الحصول على مستخدم المستشفى (مدير المستشفى)
        hospital_user = selected_hospital.user

        # إنشاء رسالة الإشعار
        message = f"🔔 *حجز جديد*\n\n"
        message += f"تم إنشاء حجز جديد من قبل المريض: {patient.user.get_full_name()}\n"
        message += f"للطبيب: {doctor.full_name}\n"
        message += f"التاريخ: {booking_date}\n"
        message += f"الوقت: {selected_shift.start_time.strftime('%H:%M')} - {selected_shift.end_time.strftime('%H:%M')}\n"
        message += f"المبلغ: {doctor_price.amount} {payment_method.payment_option.currency}\n\n"
        message += f"يرجى مراجعة تفاصيل الحجز والدفع من لوحة التحكم."

        # إنشاء الإشعار
        Notifications.objects.create(
            sender=request.user,
            user=hospital_user,
            message=message,
            notification_type='2'
        )

        # # Update shift's booked slots
        # selected_shift.booked_slots += 1
        # selected_shift.save()

        # Redirect to booking success page
        return redirect('bookings:booking_success', booking_id=booking.id,)

    context = {
        'doctor': doctor,
        'hospital_id':hospital_id,
        'selected_hospital': selected_hospital,
        'doctor_price': doctor_price,
        'selected_schedule': selected_schedule,
        'selected_shift': selected_shift,
        'booking_date': booking_date,
        'payment_methods': payment_methods
    }

    return render(request, 'frontend/home/pages/payment.html', context)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction

@require_POST
@login_required
def verify_payment(request, booking_id):
    try:
        # Use transaction to ensure data consistency
        with transaction.atomic():
            # Get booking with select_for_update to lock the record
            booking = Booking.objects.select_for_update().get(id=booking_id)
            payment = booking.payments.first()
            
            if not payment:
                return JsonResponse({
                    'status': 'error',
                    'message': 'لا يوجد سجل دفع لهذا الحجز',
                    'toast_class': 'bg-danger'
                }, status=404)
            
            # Check if payment is already verified
            if booking.payment_verified:
                return JsonResponse({
                    'status': 'error',
                    'message': 'تم التحقق من هذا الدفع مسبقاً',
                    'toast_class': 'bg-warning'
                }, status=400)
            
            # Validate payment status
            valid_statuses = [0, 2, 3]  # pending, failed, refunded
            if payment.payment_status not in valid_statuses:
                return JsonResponse({
                    'status': 'error',
                    'message': 'لا يمكن تأكيد الدفع في هذه الحالة',
                    'toast_class': 'bg-danger'
                }, status=400)
            
            # Update payment
            payment.payment_status = 1  # completed
            payment.payment_note = request.POST.get('notes', '')
            payment.save()
            
            # Update booking payment verification
            booking.payment_verified = True
            booking.payment_verified_at = timezone.now()
            booking.payment_verified_by = request.user
            
            # Update booking status if pending
            if booking.status == 'pending':
                booking.status = 'confirmed'
            
            booking.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم تأكيد الدفع بنجاح',
                'toast_class': 'bg-success',
                'verified_at': booking.payment_verified_at.strftime("%Y-%m-%d %H:%M"),
                'verified_by': booking.payment_verified_by.get_full_name()
            })
            
    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود',
            'toast_class': 'bg-danger'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'حدث خطأ أثناء معالجة الطلب',
            'toast_class': 'bg-danger',
            'debug_message': str(e)
        }, status=500)
    


@require_POST
@login_required
def reject_payment(request, booking_id):
    try:
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(id=booking_id)
            payment = booking.payments.first()
            
            if not payment:
                return JsonResponse({
                    'status': 'error',
                    'message': 'لا يوجد سجل دفع لهذا الحجز',
                    'toast_class': 'bg-danger'
                }, status=404)
            
            # Check if payment is already verified
            if booking.payment_verified:
                return JsonResponse({
                    'status': 'error',
                    'message': 'لا يمكن رفض دفعة تم التحقق منها مسبقاً',
                    'toast_class': 'bg-warning'
                }, status=400)
            
            # Validate payment status
            if payment.payment_status == 2:  # already failed
                return JsonResponse({
                    'status': 'error',
                    'message': 'هذا الدفع تم رفضه مسبقاً',
                    'toast_class': 'bg-warning'
                }, status=400)
            
            # Update payment
            payment.payment_status = 2  # failed
            payment.payment_note = request.POST.get('notes', '')
            payment.save()
            
            # Update booking status to cancelled
            booking.status = 'cancelled'
            booking.save()
            
            # Send notification to patient
            patient_user = booking.patient.user
            doctor_name = booking.doctor.full_name
            message = (
                f"⚠️ *تم رفض الدفع*\n\n"
                f"عزيزي المريض،\n"
                f"نأسف لإبلاغك أنه تم رفض الدفع الخاص بحجزك مع الدكتور {doctor_name}.\n"
                f"📅 التاريخ: {booking.booking_date}\n"
                f"🕒 الوقت: {booking.appointment_time.start_time.strftime('%H:%M')}\n\n"
                f"سبب الرفض: {payment.payment_note or 'غير محدد'}\n\n"
                f"يرجى التواصل مع إدارة المستشفى لمزيد من المعلومات."
            )
            
            Notifications.objects.create(
                sender=request.user,
                user=patient_user,
                message=message,
                notification_type='7'  # Payment rejected
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم رفض الدفع بنجاح',
                'toast_class': 'bg-success',
                'payment_status_display': payment.get_status_display()
            })
            
    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود',
            'toast_class': 'bg-danger'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'حدث خطأ أثناء معالجة الطلب',
            'toast_class': 'bg-danger',
            'debug_message': str(e)
        }, status=500)