# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from bookings.models import Booking
from hospitals.forms import DoctorForm
from payments.models import HospitalPaymentMethod, PaymentOption, PaymentStatus
from .models import Hospital, HospitalAccountRequest,HospitalDetail
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from doctors.models import Doctor,DoctorShifts,DoctorSchedules
from hospitals.models import Hospital
from doctors.models import Specialty   
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from payments.models import Payment
from bookings.models import BookingStatusHistory
from datetime import datetime, date, timedelta


def index(request):
    user = request.user
    hospital = get_object_or_404(Hospital, hospital_manager=user)
    payment_method = HospitalPaymentMethod.objects.filter(hospital=hospital)
    bookings = Booking.objects.filter(hospital=hospital)
    doctors = Doctor.objects.filter(hospitals=hospital, status=True)
    
    # جلب جميع المواعيد للمستشفى
    schedules = DoctorSchedules.objects.filter(hospital=hospital).select_related('doctor')
    doctor_schedules = {}
    
    # طباعة للتصحيح
    print("Doctors:", [f"{d.id}: {d.full_name}" for d in doctors])
    print("Schedules:", [(s.doctor.id, s.day) for s in schedules])
    
    # تنظيم المواعيد حسب الطبيب واليوم
    for schedule in schedules:
        if schedule.doctor_id not in doctor_schedules:
            doctor_schedules[schedule.doctor_id] = {}
        
        shifts = []
        for shift in schedule.shifts.all():
            shifts.append({
                'id': shift.id,
                'start_time': shift.start_time.strftime('%I:%M %p'),
                'end_time': shift.end_time.strftime('%I:%M %p'),
                'available_slots': shift.available_slots,
                'booked_slots': shift.booked_slots if hasattr(shift, 'booked_slots') else 0
            })
        doctor_schedules[schedule.doctor_id][schedule.day] = shifts
    
    # طباعة للتصحيح
    print("Doctor Schedules:", doctor_schedules)
    
    ctx = {
        "payment_options": PaymentOption.objects.filter(is_active=True),
        "payment_methods": payment_method,
        'hospital': hospital,
        'bookings': bookings,
        'doctors': doctors,
        'doctor_schedules': doctor_schedules,
        'days': DoctorSchedules.DAY_CHOICES,
    }
    return render(request, 'frontend/dashboard/hospitals/index.html', ctx)

def hospital_detail(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    return render(request, 'hospital_detail.html', {'hospital': hospital})

def hospital_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        hospital_manager_id = request.POST.get('hospital_manager_id')
        location = request.POST.get('location')
        Hospital.objects.create(name=name, hospital_manager_id=hospital_manager_id, location=location)
        return redirect('hospital_list')
    return render(request, 'hospital_form.html')

def hospital_update(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        hospital.name = request.POST['name']
        hospital.hospital_manager_id = request.POST.get('hospital_manager_id')
        hospital.location = request.POST.get('location')
        hospital.save()
        return redirect('hospital_detail', pk=hospital.pk)
    return render(request, 'hospital_form.html', {'hospital': hospital})

def hospital_delete(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        hospital.delete()
        return redirect('hospital_list')
    return render(request, 'hospital_confirm_delete.html', {'hospital': hospital})

def hospital_account_request(request):
    """معالجة طلب فتح حساب مستشفى جديد"""
    if request.method == 'POST':
        try:
            # التحقق من تطابق كلمتي المرور
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            
            if password != confirm_password:
                messages.error(request, 'كلمتا المرور غير متطابقتين')
                return render(request, 'frontend/auth/hospital-manager-register.html')

            # إنشاء طلب جديد
            hospital_request = HospitalAccountRequest(
                hospital_name=request.POST['hospital_name'],
                manager_full_name=request.POST['manager_full_name'],
                manager_email=request.POST['manager_email'],
                manager_phone=request.POST['manager_phone'],
                manager_password=password,  # تخزين كلمة المرور
                hospital_location=request.POST['hospital_location'],
                notes=request.POST.get('notes', ''),
                created_by=request.user if request.user.is_authenticated else None
            )

            # معالجة الملفات المرفقة
            if 'commercial_record' in request.FILES:
                hospital_request.commercial_record = request.FILES['commercial_record']
            if 'medical_license' in request.FILES:
                hospital_request.medical_license = request.FILES['medical_license']

            hospital_request.save()

            messages.success(request, 'تم استلام طلبك بنجاح. سنقوم بمراجعته والرد عليك قريباً')
            return redirect('hospitals:hospital_request_success')

        except Exception as e:
            messages.error(request, 'حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى')
            return render(request, 'frontend/auth/hospital-manager-register.html')

    return render(request, 'frontend/auth/hospital-manager-register.html')

def hospital_request_success(request):
    """صفحة نجاح تقديم الطلب"""
    return render(request, 'frontend/auth/hospital-request-success.html')

def hospital_request_status(request, request_id):
    """عرض حالة الطلب"""
    hospital_request = get_object_or_404(HospitalAccountRequest, id=request_id)
    return render(request, 'frontend/auth/hospital-request-status.html', {
        'request': hospital_request
    })


def add_doctor(request):
    if request.method == "POST":
        # Extract form data
        full_name = request.POST.get("full_name")
        birthday = request.POST.get("birthday")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        specialty_id = 1
        hospital_id = 1
        experience_years = request.POST.get("experience_years")
        sub_title = request.POST.get("sub_title")
        slug = request.POST.get("slug")
        about = request.POST.get("about")
        photo = request.FILES.get("photo")
        status = request.POST.get("status") == "1"
        show_at_home = request.POST.get("show_at_home") == "1"

        if not all([full_name, birthday, phone_number, email, gender, hospital_id]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            specialty = Specialty.objects.get(id=specialty_id) if specialty_id else None
            hospital = Hospital.objects.get(id=hospital_id)
        except (Specialty.DoesNotExist, Hospital.DoesNotExist):
            return HttpResponseBadRequest("Invalid specialty or hospital ID")

        doctor = Doctor.objects.create(
            full_name=full_name,
            birthday=birthday,
            phone_number=phone_number,
            email=email,
            gender=gender,
            specialty=specialty,
            experience_years=experience_years,
            sub_title=sub_title,
            slug=slug,
            about=about,
            photo=photo,
            status=status,
            show_at_home=show_at_home,
        )

        doctor.hospitals.set([hospital])  
        doctor.save()

        return render(request, "frontend/dashboard/hospitals/index.html")

    context = {
        "hospitals": Hospital.objects.all(), 
        "specialties": Specialty.objects.all(),  
    }
    return render(request, "frontend/dashboard/hospitals/index.html", context)


def add_payment_method(request):
    if request.method == "POST":
        hospital_id = 1
        payment_option_id = request.POST.get("payment_option")
        account_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        iban = request.POST.get("iban")
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "1"

        if not all([hospital_id, payment_option_id, account_name, account_number, iban, description]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            hospital = Hospital.objects.get(id=hospital_id)
            payment_option = PaymentOption.objects.get(id=payment_option_id)
        except (Hospital.DoesNotExist, PaymentOption.DoesNotExist):
            return HttpResponseBadRequest("Invalid hospital or payment option ID")

        HospitalPaymentMethod.objects.create(
            hospital=hospital,
            payment_option=payment_option,
            account_name=account_name,
            account_number=account_number,
            iban=iban,
            description=description,
            is_active=is_active,
        )

        return redirect("hospitals:index")  

    context = {
        "payment_options": PaymentOption.objects.all(),
        "hospitals": Hospital.objects.all(),  
    }
    return render(request, "frontend/dashboard/hospitals/index.html", context)



@csrf_exempt
def toggle_payment_status(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            method_id = data.get("method_id")
            is_active = data.get("is_active")

            # Validate the method ID
            method = HospitalPaymentMethod.objects.get(id=method_id)

            # Update the status
            method.is_active = is_active
            method.save()

            return JsonResponse({"message": "Status updated successfully"})
        except HospitalPaymentMethod.DoesNotExist:
            return HttpResponseBadRequest("Invalid payment method ID")
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseBadRequest("Invalid request method")


    

def accept_appointment(request, booking_id):
    """قبول الحجز """
    # التحقق من أن المستخدم هو مسؤول في المستشفى
    if not hasattr(request.user, 'hospital'):
        return JsonResponse({
            'status': 'error',
            'message': 'ليس لديك صلاحية للقيام بهذا الإجراء'
        }, status=403)

    try:
        booking = get_object_or_404(Booking, id=booking_id)
        payment = get_object_or_404(Payment, booking=booking)
        
        # التحقق من أن الحجز يتبع نفس المستشفى
        if booking.hospital != request.user.hospital:
            return JsonResponse({
                'status': 'error',
                'message': 'ليس لديك صلاحية للقيام بهذا الإجراء'
            }, status=403)
         
        # تحديث عدد الحجوزات في الفترة المحددة
        doctor_shifts = booking.appointment_time
        if doctor_shifts:
            doctor_shifts.booked_slots += 1
            doctor_shifts.save()

        booking.status = 'confirmed'
        # تحديث حالة التحقق من الدفع
        booking.payment_verified = True
        booking.payment_verified_at = timezone.now()
        booking.payment_verified_by = request.user
        booking.save()
        
        # إنشاء سجل جديد لحالة الحجز
        BookingStatusHistory.objects.create(
            booking=booking,
            status='confirmed',
            created_by=request.user,
            notes='تم قبول الحجز من قبل المستشفى'
        )
        
        # تحديث حالة الدفع
        payment.status = 'confirmed'
        payment.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'تم قبول الحجز بنجاح'
        })
        
    except (Booking.DoesNotExist, Payment.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def completed_appointment(request, booking_id):
    """تأكيد اكتمال الحجز بعد الكشف"""
    if not hasattr(request.user, 'hospital'):
        return JsonResponse({
            'status': 'error',
            'message': 'ليس لديك صلاحية للقيام بهذا الإجراء'
        }, status=403)

    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # التحقق من أن الحجز يتبع نفس المستشفى
        if booking.hospital != request.user.hospital:
            return JsonResponse({
                'status': 'error',
                'message': 'ليس لديك صلاحية للقيام بهذا الإجراء'
            }, status=403)
        
         # تحديث حالة الحجز إلى مكتمل
        booking.status = 'completed'
        booking.save()
        
        # تنقيص عدد الحجوزات في الفترة المحددة
        doctor_shifts = booking.appointment_time
        if doctor_shifts:
            doctor_shifts.booked_slots -= 1
            doctor_shifts.save()
        # إنشاء سجل جديد لحالة الحجز
        BookingStatusHistory.objects.create(
            booking=booking,
            status='completed',
            created_by=request.user,
            notes='تم تأكيد اكتمال الكشف'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'تم تأكيد اكتمال الكشف بنجاح'
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def booking_history(request, booking_id):
    """عرض تاريخ حالات الحجز"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'يجب تسجيل الدخول أولاً'
        }, status=401)

    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # التحقق من الصلاحيات - يجب أن يكون المستخدم إما صاحب الحجز أو من المستشفى
        if not (hasattr(request.user, 'hospital') and booking.hospital == request.user.hospital) and \
           not (hasattr(request.user, 'patients') and booking.patient.user == request.user):
            return JsonResponse({
                'status': 'error',
                'message': 'ليس لديك صلاحية للوصول إلى هذه المعلومات'
            }, status=403)

        # جلب تاريخ الحالات مرتباً من الأحدث إلى الأقدم
        history = booking.status_history.all().select_related('created_by').order_by('-created_at')
        
        # تحويل البيانات إلى تنسيق JSON
        history_data = [{
            'status': item.status,
            'notes': item.notes,
            'created_by': item.created_by.get_full_name() if item.created_by else 'غير معروف',
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for item in history]

        return JsonResponse({
            'status': 'success',
            'booking_id': booking_id,
            'patient_name': booking.patient.full_name,
            'doctor_name': booking.doctor.full_name,
            'history': history_data
        })

    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def delete_booking(request, booking_id):
    """حذف الحجز"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'يجب تسجيل الدخول أولاً'
        }, status=401)

    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # التحقق من الصلاحيات
        if not hasattr(request.user, 'hospital') or booking.hospital != request.user.hospital:
            return JsonResponse({
                'status': 'error',
                'message': 'ليس لديك صلاحية للقيام بهذا الإجراء'
            }, status=403)

        # إنشاء سجل جديد لحالة الحجز قبل الحذف
        BookingStatusHistory.objects.create(
            booking=booking,
            status='cancelled',
            created_by=request.user,
            notes='تم حذف الحجز'
        )
        
        # تحديث حالة الحجز إلى ملغي بدلاً من حذفه فعلياً
        booking.status = 'cancelled'
        booking.save()

        return JsonResponse({
            'status': 'success',
            'message': 'تم إلغاء الحجز بنجاح'
        })

    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def edit_booking(request, booking_id):
    """تعديل الحجز"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'يجب تسجيل الدخول أولاً'
        }, status=401)

    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # التحقق من الصلاحيات
        if not hasattr(request.user, 'hospital') or booking.hospital != request.user.hospital:
            return JsonResponse({
                'status': 'error',
                'message': 'ليس لديك صلاحية للقيام بهذا الإجراء'
            }, status=403)

        if request.method == 'POST':
            data = json.loads(request.body)
            
            # تحديث البيانات القابلة للتعديل
            if 'amount' in data:
                booking.amount = data['amount']
            if 'is_online' in data:
                booking.is_online = data['is_online']
            if 'payment_notes' in data:
                booking.payment_notes = data['payment_notes']
            
            booking.save()

            # إنشاء سجل جديد لحالة الحجز
            BookingStatusHistory.objects.create(
                booking=booking,
                status=booking.status,
                created_by=request.user,
                notes='تم تعديل بيانات الحجز'
            )

            return JsonResponse({
                'status': 'success',
                'message': 'تم تعديل الحجز بنجاح'
            })
        else:
            # إرجاع بيانات الحجز للعرض في نموذج التعديل
            schedule = booking.appointment_date
            shift = booking.appointment_time
            
            return JsonResponse({
                'status': 'success',
                'booking': {
                    'id': booking.id,
                    'amount': str(booking.amount),
                    'is_online': booking.is_online,
                    'payment_notes': booking.payment_notes or '',
                    'patient_name': booking.patient.full_name,
                    'doctor_name': booking.doctor.full_name,
                    'appointment_date': schedule.get_day_display(),
                    'appointment_time': f"{shift.start_time} - {shift.end_time}"
                }
            })

    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def schedule_timings(request):
    try:
        hospital = get_object_or_404(Hospital, hospital_manager=request.user)
        context = {
            'doctors': Doctor.objects.filter(hospitals=hospital, status=True),
            'days': DoctorSchedules.DAY_CHOICES
        }
        
        if request.method == 'POST':
            doctor_id = request.POST.get('doctor_id')
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            slot_duration = request.POST.get('slot_duration', 30)
            
            doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
            
            # إنشاء أو الحصول على جدول الطبيب
            schedule, created = DoctorSchedules.objects.get_or_create(
                doctor=doctor,
                hospital=hospital,
                day=day
            )
            
            # حساب عدد المواعيد المتاحة
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
            duration = timedelta(minutes=int(slot_duration))
            total_time = datetime.combine(date.today(), end) - datetime.combine(date.today(), start)
            available_slots = total_time.seconds // duration.seconds
            
            # إنشاء الفترة الزمنية
            shift = DoctorShifts.objects.create(
                doctor_schedule=schedule,
                start_time=start,
                end_time=end,
                available_slots=available_slots
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم إضافة الموعد بنجاح',
                'shift': {
                    'id': shift.id,
                    'start_time': shift.start_time.strftime('%I:%M %p'),
                    'end_time': shift.end_time.strftime('%I:%M %p'),
                    'available_slots': shift.available_slots
                }
            })
        
        return render(request, 'frontend/dashboard/hospitals/sections/schedule-timings.html', context)
    
    except Exception as e:
        messages.error(request, f'حدث خطأ: {str(e)}')
        return HttpResponseBadRequest(str(e))

@login_required
def delete_shift(request, shift_id):
    try:
        hospital = get_object_or_404(Hospital, hospital_manager=request.user)
        shift = get_object_or_404(DoctorShifts, id=shift_id, doctor_schedule__hospital=hospital)
        shift.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'تم حذف الموعد بنجاح'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
