from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from blog.forms import PostForm
from blog.models import Post, Tag,Category
from payments.models import Payment, PaymentStatus
from bookings.models import BookingStatusHistory
from bookings.models import Booking
from payments.models import (
    HospitalPaymentMethod,
    PaymentOption,
    Payment,
)
from hospitals.models import Hospital, HospitalAccountRequest
from doctors.models import (
    Doctor,
    DoctorPricing,
    DoctorSchedules,
    Specialty,
)
from django.core.paginator import Paginator
from datetime import datetime, date, timedelta
from django.db.models import Sum

def index(request):
    user = request.user
    hospital = get_object_or_404(Hospital, hospital_manager=user)
    payment_method = HospitalPaymentMethod.objects.filter(hospital=hospital)
    bookings = Booking.objects.filter(hospital=hospital)
    doctors = Doctor.objects.filter(hospitals=hospital, status=True)
    
    # Get current date and first day of month
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Get all specialties in the hospital
    specialties = Specialty.objects.filter(doctor__hospitals=hospital).distinct()
    total_specialties = specialties.count()
    specialties_count_percentage = min((total_specialties / 10) * 100, 100)  # Assuming 10 is the target
    
    # Get monthly revenue
    monthly_revenue = Payment.objects.filter(
        booking__hospital=hospital,
        payment_date__year=today.year,
        payment_date__month=today.month,
        payment_status__status_code=2
    ).aggregate(total=Sum('payment_totalamount'))['total'] or 0
    
    # Calculate revenue percentage (compared to target)
    monthly_target = 50000  # مثال للهدف الشهري
    revenue_percentage = min((monthly_revenue / monthly_target) * 100, 100)
    
    # Get appointments statistics
    total_appointments = bookings.filter(
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    
    appointments_target = 100  # مثال للهدف
    appointments_percentage = min((total_appointments / appointments_target) * 100, 100)
    
    # Get latest appointments
    latest_appointments = bookings.select_related(
        'doctor', 'doctor__specialty', 'patient'
    ).order_by('-created_at')[:10]
    
    # Get latest doctors with ratings
    latest_doctors = doctors.select_related('specialty').prefetch_related('reviews').order_by('-created_at')[:10]
    
    # Calculate today's appointments for each doctor
    for doctor in latest_doctors:
        doctor.today_appointments_count = bookings.filter(
            doctor=doctor,
            booking_date=today
        ).count()
        
        # Calculate average rating
        reviews = doctor.reviews.all()
        if reviews:
            doctor.average_rating = sum(review.rating for review in reviews) / len(reviews)
        else:
            doctor.average_rating = 0
    
    # Get latest payments
    latest_payments = Payment.objects.filter(
        booking__hospital=hospital
    ).select_related(
        'booking__doctor', 
        'booking__patient',
        'payment_method'
    ).order_by('-payment_date')[:10]
    
    # Get Arabic month name
    ARABIC_MONTHS = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "إبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }
    current_month_name = ARABIC_MONTHS[today.month]
    
    # Get payment statuses for the filter dropdown
    payment_statuses = PaymentStatus.objects.all()
    
    # Get invoices with filters
    invoices = Payment.objects.filter(booking__hospital=hospital).select_related('booking', 'booking__patient')
    
    # Apply filters if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    payment_status = request.GET.get('payment_status')
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')
    
    if date_from:
        invoices = invoices.filter(payment_date__gte=date_from)
    if date_to:
        invoices = invoices.filter(payment_date__lte=date_to)
    if payment_status:
        invoices = invoices.filter(payment_status_id=payment_status)
    if amount_min:
        invoices = invoices.filter(payment_totalamount__gte=amount_min)
    if amount_max:
        invoices = invoices.filter(payment_totalamount__lte=amount_max)
        
    # Order by latest first
    invoices = invoices.order_by('-payment_date')

    # جلب جميع المواعيد للمستشفى
    schedules = DoctorSchedules.objects.filter(hospital=hospital).select_related('doctor')
    doctor_schedules = {}
    
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
    
    # إحصائيات الحجوزات
    bookings_stats = {
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
    }

    # إحصائيات المدفوعات
    payment_stats = {
        'total_invoices_count': invoices.count(),
        'total_paid_amount': invoices.filter(payment_status__status_code=2).aggregate(
            total=Sum('payment_totalamount'))['total'] or 0,
        'pending_payments_count': invoices.filter(payment_status__status_code=1).count(),
        'total_pending_amount': invoices.filter(payment_status__status_code=1).aggregate(
            total=Sum('payment_totalamount'))['total'] or 0,
    }
    
    ctx = {
        "payment_options": PaymentOption.objects.filter(is_active=True),
        "payment_methods": payment_method,
        'hospital': hospital,
        'bookings': bookings,
        'doctors': doctors,
        'doctor_schedules': doctor_schedules,
        'days': DoctorSchedules.DAY_CHOICES,
        'invoices': invoices,
        'payment_statuses': payment_statuses,
        'specialties': specialties,
        'specialties_count_percentage': specialties_count_percentage,
        'total_revenue': monthly_revenue,
        'revenue_percentage': revenue_percentage,
        'total_appointments': total_appointments,
        'appointments_percentage': appointments_percentage,
        'latest_appointments': latest_appointments,
        'latest_doctors': latest_doctors,
        'latest_payments': latest_payments,
        'current_month_name': current_month_name,
        **payment_stats,
        **bookings_stats,
    }
    
    return render(request, 'frontend/dashboard/hospitals/index.html', ctx)


@login_required
def blog_list(request):
    user = request.user
    hospital = get_object_or_404(Hospital, hospital_manager=user)
    posts = Post.objects.filter(author=hospital)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'allBlogs': page_obj,
    }
    return render(request, 'frontend/dashboard/hospitals/sections/hospital_blogs.html', context)

@login_required
def blog_pending_list(request):
    user = request.user
    hospital = get_object_or_404(Hospital, hospital_manager=user)
    posts = Post.objects.filter(author=hospital)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'allBlogs': page_obj,
    }
    return render(request, 'frontend/dashboard/hospitals/sections/hospital_pending_blog.html', context)



@login_required
def add_blog(request):
    user = request.user
    hospital = get_object_or_404(Hospital, hospital_manager=user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.author = hospital
            new_blog.save()
            form.save_m2m() 
            messages.success(request, 'Blog added successfully!')
            return redirect('hospitals:blog_list') 
    else:
        form = PostForm()

    tags = Tag.objects.filter(status=True)
    categories = Category.objects.filter(status=True)

    context = {
        'form': form,
        'tags': tags,
        'categories': categories,
    }
    return render(request, 'frontend/dashboard/hospitals/sections/hospitals-add-blog.html', context)

@login_required
def edit_blog(request, blog_id):
    user = request.user
    hospital = get_object_or_404(Hospital, hospital_manager=user)
    blog = get_object_or_404(Post, id=blog_id, author=hospital)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            updated_blog = form.save(commit=False)  
            updated_blog.save()  
            form.save_m2m()  
            messages.success(request, 'Blog updated successfully!')
            return redirect('hospitals:blog_list') 
    else:
        form = PostForm(instance=blog)

    tags = Tag.objects.filter(status=True)
    categories = Category.objects.filter(status=True)

    context = {
        'form': form,
        'tags': tags,
        'categories': categories,
        'blog': blog,
    }
    return render(request, 'frontend/dashboard/hospitals/sections/hospitals-edit-blog.html', context)




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
        payment.payment_status = PaymentStatus.objects.get(status_code=2)
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
        hospital = Hospital.objects.get(hospital_manager=request.user)
        
        if request.method == 'POST':
            doctor_id = request.POST.get('doctor_id')
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            max_appointments = int(request.POST.get('max_appointments', 1))

            doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
            
            # إنشاء أو الحصول على جدول الطبيب
            schedule, created = DoctorSchedules.objects.get_or_create(
                doctor=doctor,
                hospital=hospital,
                day=day
            )
            
            # إنشاء الفترة الزمنية
            shift = DoctorShifts.objects.create(
                doctor_schedule=schedule,
                start_time=start_time,
                end_time=end_time,
                available_slots=max_appointments,
                booked_slots=0
            )

            return JsonResponse({
                'status': 'success',
                'message': 'تم إضافة الموعد بنجاح',
                'shift': {
                    'id': shift.id,
                    'start_time': shift.start_time.strftime('%H:%M'),
                    'end_time': shift.end_time.strftime('%H:%M'),
                    'available_slots': shift.available_slots,
                    'booked_slots': shift.booked_slots
                }
            })

        # GET request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            doctor_id = request.GET.get('doctor_id')
            if doctor_id:
                doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
                schedules = DoctorShifts.objects.filter(
                    doctor_schedule__doctor=doctor,
                    doctor_schedule__hospital=hospital
                ).select_related('doctor_schedule')
                
                # تنظيم المواعيد حسب اليوم
                doctor_schedules = {}
                for shift in schedules:
                    day = shift.doctor_schedule.day
                    if day not in doctor_schedules:
                        doctor_schedules[day] = []
                    
                    doctor_schedules[day].append({
                        'id': shift.id,
                        'start_time': shift.start_time.strftime('%H:%M'),
                        'end_time': shift.end_time.strftime('%H:%M'),
                        'available_slots': shift.available_slots,
                        'booked_slots': shift.booked_slots
                    })
                
                return JsonResponse({
                    'status': 'success',
                    'schedules': {
                        str(doctor_id): doctor_schedules
                    }
                })
            return JsonResponse({'status': 'error', 'message': 'معرف الطبيب مطلوب'})

        # عرض الصفحة
        doctors = Doctor.objects.filter(hospitals=hospital)
        schedules = DoctorShifts.objects.filter(
            doctor_schedule__hospital=hospital
        ).select_related('doctor_schedule__doctor')
        
        # تنظيم المواعيد حسب الطبيب واليوم
        doctor_schedules = {}
        for shift in schedules:
            doctor_id = shift.doctor_schedule.doctor.id
            day = shift.doctor_schedule.day
            
            if doctor_id not in doctor_schedules:
                doctor_schedules[doctor_id] = {}
            
            if day not in doctor_schedules[doctor_id]:
                doctor_schedules[doctor_id][day] = []
            
            doctor_schedules[doctor_id][day].append({
                'id': shift.id,
                'start_time': shift.start_time.strftime('%H:%M'),
                'end_time': shift.end_time.strftime('%H:%M'),
                'available_slots': shift.available_slots,
                'booked_slots': shift.booked_slots
            })

        context = {
            'doctors': doctors,
            'doctor_schedules': doctor_schedules,
            'days': DoctorSchedules.DAY_CHOICES,
            'section': 'schedule_timings'
        }
        
        return render(request, 'frontend/dashboard/hospitals/index.html', context)

    except Hospital.DoesNotExist:
        messages.error(request, 'لا يمكنك الوصول إلى هذه الصفحة')
        return redirect('home')
    except Exception as e:
        print(f"Error: {str(e)}")  # للتصحيح
        messages.error(request, 'حدث خطأ أثناء معالجة الطلب')
        return redirect('home')

@login_required
def delete_shift(request, shift_id):
    if request.method == 'POST':
        try:
            hospital = get_object_or_404(Hospital, hospital_manager=request.user)
            shift = get_object_or_404(DoctorShifts, 
                id=shift_id, 
                doctor_schedule__hospital=hospital
            )
            shift.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'تم حذف الموعد بنجاح'
            })
        except (Hospital.DoesNotExist, DoctorShifts.DoesNotExist):
            return JsonResponse({
                'status': 'error',
                'message': 'لا يمكنك حذف هذا الموعد'
            }, status=403)
        except Exception as e:
            print(f"Error: {str(e)}")  # للتصحيح
            return JsonResponse({
                'status': 'error',
                'message': 'حدث خطأ أثناء حذف الموعد'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'طريقة الطلب غير صحيحة'
    }, status=405)

@login_required
def filter_invoices(request):
    """تصفية الفواتير"""
    hospital = request.user.hospital
    invoices = Payment.objects.filter(payment_method__hospital=hospital)
    
    # إحصائيات سريعة
    context = {
       
    }
    
    # تطبيق الفلترة
    date_from = request.GET.get('date_from')
    if date_from:
        invoices = invoices.filter(payment_date__date__gte=date_from)
        
    date_to = request.GET.get('date_to')
    if date_to:
        invoices = invoices.filter(payment_date__date__lte=date_to)
        
    payment_status = request.GET.get('payment_status')
    if payment_status:
        invoices = invoices.filter(payment_status__id=payment_status)
        
    amount_min = request.GET.get('amount_min')
    if amount_min:
        invoices = invoices.filter(payment_totalamount__gte=amount_min)
        
    amount_max = request.GET.get('amount_max')
    if amount_max:
        invoices = invoices.filter(payment_totalamount__lte=amount_max)

    # تحديث الإحصائيات بعد التصفية
    context.update({
        'invoices': invoices.order_by('-payment_date'),
        'payment_statuses': PaymentStatus.objects.all()
    })
    
    return render(request, 'frontend/dashboard/hospitals/sections/invoice_table.html', context)

@login_required
def invoice_detail(request, invoice_id):
    user = request.user
    hospital = get_object_or_404(Hospital, hospital_manager=user)
    
    # Get the invoice with related data
    invoice = get_object_or_404(
        Payment.objects.select_related(
            'booking',
            'booking__patient',
            'booking__doctor',
            'payment_status',
            'payment_method',
            'payment_method__payment_option'
        ),
        id=invoice_id,
        booking__hospital=hospital
    )
    
    context = {
        'invoice': invoice,
        'hospital': hospital,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If AJAX request, return only the modal content
        return render(request, 'frontend/dashboard/hospitals/sections/invoice_detail_modal.html', context)
    
    # If regular request, return the full page
    return render(request, 'frontend/dashboard/hospitals/invoice_detail.html', context)

@login_required
def hospital_dashboard(request):
    """عرض لوحة تحكم المستشفى"""
    
    # Get the current hospital
    hospital = get_object_or_404(Hospital, hospital_manager=request.user)
    
    # Get current date and first day of month
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Get all specialties in the hospital
    specialties = Specialty.objects.filter(doctor__hospitals=hospital).distinct()
    total_specialties = specialties.count()
    specialties_count_percentage = min((total_specialties / 10) * 100, 100)  # Assuming 10 is the target number of specialties
    
    # Get monthly revenue
    monthly_revenue = Payment.objects.filter(
        booking__hospital=hospital,
        payment_date__year=today.year,
        payment_date__month=today.month,
        payment_status__status_code=2
    ).aggregate(total=Sum('payment_totalamount'))['total'] or 0
    
    # Calculate revenue percentage (compared to target)
    monthly_target = 50000  # Example target
    revenue_percentage = min((monthly_revenue / monthly_target) * 100, 100)
    
    # Get appointments statistics
    total_appointments = Booking.objects.filter(
        hospital=hospital,
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    
    appointments_target = 100  # Example target
    appointments_percentage = min((total_appointments / appointments_target) * 100, 100)
    
    # Get latest appointments
    latest_appointments = Booking.objects.filter(
        hospital=hospital
    ).select_related(
        'doctor', 'doctor__specialty', 'patient'
    ).order_by('-created_at')[:10]
    
    # Get latest doctors
    latest_doctors = Doctor.objects.filter(
        hospitals=hospital
    ).select_related('specialty').prefetch_related('reviews').order_by('-created_at')[:10]
    
    # Calculate today's appointments for each doctor
    for doctor in latest_doctors:
        doctor.today_appointments_count = Booking.objects.filter(
            doctor=doctor,
            booking_date=today
        ).count()
        
        # Calculate average rating
        reviews = doctor.reviews.all()
        if reviews:
            doctor.average_rating = sum(review.rating for review in reviews) / len(reviews)
        else:
            doctor.average_rating = 0
    
    # Get latest payments
    latest_payments = Payment.objects.filter(
        booking__hospital=hospital
    ).select_related(
        'booking__doctor', 
        'booking__patient',
        'payment_method'
    ).order_by('-payment_date')[:10]
    
    # Get Arabic month name
    ARABIC_MONTHS = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "إبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }
    current_month_name = ARABIC_MONTHS[today.month]
    
    context = {
        'hospital': hospital,
        'specialties': specialties,
        'specialties_count_percentage': specialties_count_percentage,
        'total_revenue': monthly_revenue,
        'revenue_percentage': revenue_percentage,
        'total_appointments': total_appointments,
        'appointments_percentage': appointments_percentage,
        'latest_appointments': latest_appointments,
        'latest_doctors': latest_doctors,
        'latest_payments': latest_payments,
        'current_month_name': current_month_name,
    }
    
    return render(request, 'frontend/dashboard/hospitals/sections/hospitals-dashboard.html', context)
