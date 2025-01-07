from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery, Max
import json
from bookings.models import Booking
from payments.models import (
    HospitalPaymentMethod,
    PaymentOption,
    PaymentStatus,
    Payment,
)
from hospitals.models import Hospital, HospitalAccountRequest
from doctors.models import (
    Doctor,
    DoctorPricing,
    Specialty,
)


@login_required
def index(request):
    user = request.user
    hospital=get_object_or_404(Hospital,hospital_manager=user)
    speciality=Specialty.objects.filter(status=True)
    payment_method = HospitalPaymentMethod.objects.filter(hospital=hospital)
    bookings = Booking.objects.filter(hospital=hospital)

    book = user.groups.all()[0] 
    print("--------------------")
    print(user.groups.all()[0])
    print(book.permissions.all())
    print("--------------------")
    ctx  = {
        "payment_options": PaymentOption.objects.filter(is_active=True),
        "payment_methods": payment_method,
        'hospital':hospital,
        'speciality':speciality,
        'bookings': bookings,
        'hospital': hospital
    }
    return render(request, 'frontend/dashboard/hospitals/index.html',ctx)

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
        full_name = request.POST.get("full_name")
        birthday = request.POST.get("birthday")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        specialty_id = request.POST.get("specialty")
        hospital_id = request.user.id
        experience_years = request.POST.get("experience_years")
        sub_title = request.POST.get("sub_title")
        slug = request.POST.get("slug")
        about = request.POST.get("about")
        photo = request.FILES.get("photo")
        status = request.POST.get("status") == "1"
        show_at_home = request.POST.get("show_at_home") == "1"
        price = request.POST.get("price")

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
        priceCreate = DoctorPricing.objects.create(
            doctor = get_object_or_404(Doctor,id=doctor.id),
            hospital = get_object_or_404(Hospital,id=hospital_id),
            amount = price,
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
    """قبول الحجز وتحديث حالته"""
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

        # تحديث حالة الحجز إلى مؤكد
        booking.status = 'confirmed'
        
        # تحديث عدد الحجوزات في الفترة المحددة
        doctor_shifts = booking.appointment_time
        if doctor_shifts:
            doctor_shifts.booked_slots += 1
            doctor_shifts.save()
        
        # تحديث حالة التحقق من الدفع
        booking.payment_verified = True
        booking.payment_verified_at = timezone.now()
        booking.payment_verified_by = request.user
        booking.save()
        
        # تحديث حالة الدفع إلى مكتمل
        payment.payment_status = get_object_or_404(PaymentStatus, status_code=2)
        payment.save()

        messages.success(request, 'تم قبول الحجز والدفع بنجاح')
        return JsonResponse({
            'status': 'success',
            'message': 'تم قبول الحجز وتأكيد الدفع بنجاح',
            'booking_id': booking_id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

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
        messages.success(request, 'تم تأكيد اكتمال الحجز بنجاح')
        return JsonResponse({
            'status': 'success',
            'message': 'تم تأكيد اكتمال الحجز بنجاح',
            'booking_id': booking_id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

    


