from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, date, time
from django.db.models import Prefetch
from doctors.models import Doctor, DoctorSchedules, DoctorShifts, DoctorPricing
from hospitals.models import Hospital
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import models
from blog.forms import PostForm
from blog.models import Post, Tag,Category
from patients.models import Patients
from payments.models import Payment
from bookings.models import BookingStatusHistory
from bookings.models import Booking
from payments.models import (
    HospitalPaymentMethod,
    PaymentOption,
    Payment,
)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import HospitalAccountRequest, HospitalUpdateRequest, PhoneNumber
from django.conf import settings
from hospitals.models import City, Hospital, HospitalAccountRequest
from doctors.models import (
    Doctor,
    DoctorPricing,
    DoctorSchedules,
    DoctorShifts,
    Specialty,
)
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from blog.forms import PostForm
from blog.models import Post, Tag,Category
from payments.models import Payment
from bookings.models import BookingStatusHistory
from bookings.models import Booking
from notifications.models import Notifications
from django.contrib.auth import get_user_model
from .forms import NotificationForm
from users.models import CustomUser
from payments.models import (
    HospitalPaymentMethod,
    PaymentOption,
    Payment,
)
from hospitals.models import Hospital, HospitalAccountRequest
from doctors.models import (
    Doctor,
    DoctorPricing,
    Specialty,
    DoctorPricingHistory
)
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from decimal import Decimal
import uuid

User = get_user_model()

@login_required(login_url='/user/login')
def index(request):
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)  
    speciality = Specialty.objects.filter(status=True)
    payment_method = HospitalPaymentMethod.objects.filter(hospital=hospital)
    bookings = Booking.objects.filter(hospital=hospital)
    doctors = Doctor.objects.filter(hospitals=hospital).select_related('specialty').prefetch_related(
        Prefetch('pricing', queryset=DoctorPricing.objects.filter(hospital=hospital))
    )
    phoneNumber = PhoneNumber.objects.filter(hospital=hospital)
    city = City.objects.filter( status=True)
    patients = Patients.objects.filter(bookings__hospital_id=user.id).distinct()

    
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
        payment_status=2
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
    
    # Get latest doctors with ratings and today's appointments
    latest_doctors = list(doctors.select_related('specialty').prefetch_related('reviews')[:10])
    doctor_ids = [doctor.id for doctor in latest_doctors]
    
    # Get today's appointments count for each doctor using a single query
    today_appointments = bookings.filter(
        doctor_id__in=doctor_ids,
        booking_date=today
    ).values('doctor').annotate(count=Count('id'))
    
    # Create a dictionary of doctor_id: appointment_count
    appointments_dict = {item['doctor']: item['count'] for item in today_appointments}
    
    # Assign the count to each doctor
    for doctor in latest_doctors:
        doctor.today_appointments_count = appointments_dict.get(doctor.id, 0)
        
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
    
    # Get invoices with filters
    invoices = Payment.objects.filter(booking__hospital=hospital).select_related('booking', 'booking__patient')
    
    # Apply filters if provided
    date_from = request.GET.get('date_from')
    if date_from:
        invoices = invoices.filter(payment_date__gte=date_from)
    date_to = request.GET.get('date_to')
    if date_to:
        invoices = invoices.filter(payment_date__lte=date_to)
    payment_status = request.GET.get('payment_status')
    if payment_status:
        invoices = invoices.filter(payment_status_id=payment_status)
    amount_min = request.GET.get('amount_min')
    if amount_min:
        invoices = invoices.filter(payment_totalamount__gte=amount_min)
    amount_max = request.GET.get('amount_max')
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
        'total_paid_amount': invoices.filter(payment_status=2).aggregate(
            total=Sum('payment_totalamount'))['total'] or 0,
        'pending_payments_count': invoices.filter(payment_status=1).count(),
        'total_pending_amount': invoices.filter(payment_status=1).aggregate(
            total=Sum('payment_totalamount'))['total'] or 0,
    }
    
    bookings = Booking.objects.filter(hospital=hospital)

    # معالجة طلب الحذف إذا كان الطلب POST وفيه notification_id
    if request.method == 'POST' and 'notification_id' in request.body.decode('utf-8'):
        import json
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        result = delete_notification(notification_id, user)
        return JsonResponse(result)

    # جلب الإشعارات
    notifications = get_notifications_for_user(user)
    hospital_notifications_sended = get_notifications_sended_from(user)

    # حساب عدد الإشعارات غير المقروءة
    unread_notifications_count = notifications.filter(status='0').count()

    context = {
        "payment_options": PaymentOption.objects.filter(is_active=True),
        "payment_methods": payment_method,
        'hospital': hospital,
        'users': User.objects.all(),
        'bookings': bookings,
        'city':city,
        'doctors': doctors,
        'patients':patients,
        'speciality':Specialty.objects.filter(status=True),
        'doctor_schedules': doctor_schedules,
        'days': DoctorSchedules.DAY_CHOICES,
        'invoices': invoices,
        'payment_statuses': Payment.PaymentStatus_choices,
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
        'total_doctors': doctors.count(),
        'active_doctors': doctors.filter(status=True).count(),
        'specialties_count': Specialty.objects.filter(
            doctor__hospitals=hospital
        ).distinct().count(),
        'hospitals_count': hospital.count() if isinstance(hospital, models.QuerySet) else 1,
        **payment_stats,
        **bookings_stats,
        'hospital': hospital,
        'speciality': speciality,
        'bookings': bookings,
        'notifications': notifications,
        'hospital_notifications_sended':hospital_notifications_sended,
        'unread_notifications_count': unread_notifications_count,
    }
    
    return render(request, 'frontend/dashboard/hospitals/index.html', context)


@login_required(login_url='/user/login')

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

@login_required(login_url='/user/login')

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



@login_required(login_url='/user/login')

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

@login_required(login_url='/user/login')

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




#الاشعارات
def get_notifications_for_user(user):
    """
    دالة لجلب الإشعارات الخاصة بالمستخدم.
    """
    notifications = Notifications.objects.filter(user=user, is_active=True).order_by('-send_time')
    return notifications

def get_notifications_sended_from(user):
    """
        get all notifications that hospital sended
    """
    notifications = Notifications.objects.filter(sender=user, is_active=True).order_by('-send_time')
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




@login_required(login_url='/user/login')

def blog_list(request):
    user = request.user
    hospital = get_object_or_404(Hospital, user_id=user)
    posts = Post.objects.filter(author=hospital)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'allBlogs': page_obj,
    }
    return render(request, 'frontend/dashboard/hospitals/sections/hospital_blogs.html', context)

@login_required(login_url='/user/login')

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



@login_required(login_url='/user/login')

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

@login_required(login_url='/user/login')

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



def hospital_request_success(request):
    """صفحة نجاح تقديم الطلب"""
    return render(request, 'frontend/auth/hospital-request-success.html')

def hospital_request_status(request, request_id):
    """عرض حالة الطلب"""
    hospital_request = get_object_or_404(HospitalAccountRequest, id=request_id)
    return render(request, 'frontend/auth/hospital-request-status.html', {
        'request': hospital_request
    })




@login_required(login_url='/user/login')

def filter_doctors(request):
    hospital = get_object_or_404(Hospital, hospital_manager=request.user)
    
    # Get all doctors for this hospital
    doctors = Doctor.objects.filter(hospitals=hospital)
    
    # Apply filters
    specialty = request.GET.get('specialty')
    if specialty:
        doctors = doctors.filter(specialty_id=specialty)
        
    gender = request.GET.get('gender')
    if gender:
        doctors = doctors.filter(gender=gender)
        
    status = request.GET.get('status')
    if status:
        doctors = doctors.filter(status=status == '1')
        
    search = request.GET.get('search')
    if search:
        doctors = doctors.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone_number__icontains=search)
        )
    
    experience_min = request.GET.get('experience_min')
    if experience_min:
        doctors = doctors.filter(experience_years__gte=experience_min)
        
    experience_max = request.GET.get('experience_max')
    if experience_max:
        doctors = doctors.filter(experience_years__lte=experience_max)

    # Get pricing history
    pricing_history = DoctorPricing.objects.filter(
        hospital=hospital
    ).select_related('doctor').order_by('-created_at')[:10]  # Show last 10 changes
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(doctors.order_by('-created_at'), 10) 
    
    try:
        doctors = paginator.page(page)
    except PageNotAnInteger:
        doctors = paginator.page(1)
    except EmptyPage:
        doctors = paginator.page(paginator.num_pages)

    context = {
        'doctors': doctors,
        'specialties': Specialty.objects.all(),
        'pricing_history': pricing_history,
        'request': request, 
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'frontend/dashboard/hospitals/sections/doctor_table.html', context)
    
    return render(request, 'frontend/dashboard/hospitals/index.html', context)


@login_required(login_url='/user/login')
def add_doctor(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        birthday = request.POST.get("birthday")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        specialty_id = request.POST.get("specialty")
        experience_years = request.POST.get("experience_years")
        sub_title = request.POST.get("sub_title")
        slug = request.POST.get("slug")
        about = request.POST.get("about")
        photo = request.FILES.get("photo")
        status = request.POST.get("status") == "1"
        show_at_home = request.POST.get("show_at_home") == "1"
        amount = request.POST.get("amount")

        if not all([full_name, birthday, phone_number, email, gender, specialty_id]):
            messages.error(request, "الرجاء تعبئة جميع الحقول المطلوبة")
            return redirect('hospitals:add_doctor_form')

        try:
            hospital = get_object_or_404(Hospital, user=request.user)
            specialty = get_object_or_404(Specialty, id=specialty_id)
            
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
            
            DoctorPricing.objects.create(
                doctor=doctor,
                hospital=hospital,
                amount=amount,
            )
            
            doctor.hospitals.add(hospital)
            doctor.save()
            
            messages.success(request, "تم إضافة الطبيب بنجاح")
            return redirect('hospitals:index')
            
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء إضافة الطبيب: {str(e)}")
            return redirect('hospitals:add_doctor_form')

    return redirect('hospitals:index')


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



def update_payment_method(request):
    if request.method == "POST":
        method_id = request.POST.get("method_id")
        account_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        iban = request.POST.get("iban")
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "1"

        if not all([method_id, account_name, account_number, iban, description]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            payment_method = HospitalPaymentMethod.objects.get(id=method_id)
        except HospitalPaymentMethod.DoesNotExist:
            return HttpResponseBadRequest("Payment method not found")

        payment_method.account_name = account_name
        payment_method.account_number = account_number
        payment_method.iban = iban
        payment_method.description = description
        payment_method.is_active = is_active
        payment_method.save()

        return redirect("hospitals:index")

    return HttpResponseBadRequest("Invalid request method")



@csrf_exempt
def delete_payment_method(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            hospital_id = data.get("hospital_id")
            payment_method_id = data.get("payment_method_id")
            
            payment_method = HospitalPaymentMethod.objects.filter(hospital_id=hospital_id, id=payment_method_id).first()
            
            if payment_method:
                payment_method.delete()  
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error", "message": "Payment method not found."}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


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
        payment.payment_status = 2
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

@login_required(login_url='/user/login')
@csrf_exempt
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

@login_required(login_url='/user/login')

def schedule_timings(request):
    try:
        hospital = Hospital.objects.get(hospital_manager=request.user)
        
        if request.method == 'POST':
            doctor_id = request.POST.get('doctor_id')
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            max_appointments = int(request.POST.get('max_appointments', 1))

            # التحقق من صحة البيانات
            if not all([doctor_id, day, start_time, end_time]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'جميع الحقول مطلوبة'
                })

            try:
                # التحقق من وجود الطبيب وارتباطه بالمستشفى
                doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
                
                # التحقق من صحة التوقيت
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                
                if start_time_obj >= end_time_obj:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'وقت البداية يجب أن يكون قبل وقت النهاية'
                    })

                # التحقق من تداخل المواعيد
                existing_shifts = DoctorShifts.objects.filter(
                    doctor_schedule__doctor=doctor,
                    doctor_schedule__day=day,
                    doctor_schedule__hospital=hospital
                )
                
                for shift in existing_shifts:
                    if (start_time_obj <= shift.end_time and end_time_obj >= shift.start_time):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'يوجد تداخل مع موعد آخر'
                        })

                # إنشاء أو الحصول على جدول الطبيب
                schedule, created = DoctorSchedules.objects.get_or_create(
                    doctor=doctor,
                    hospital=hospital,
                    day=day
                )
                
                # إنشاء الفترة الزمنية
                shift = DoctorShifts.objects.create(
                    doctor_schedule=schedule,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
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
                
            except (ValueError, Doctor.DoesNotExist) as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })

        # GET request
        doctors = Doctor.objects.filter(hospitals=hospital)
        schedules = DoctorShifts.objects.filter(
            doctor_schedule__hospital=hospital
        ).select_related('doctor_schedule__doctor')
        
        context = {
            'doctors': doctors,
            'doctor_schedules': {},
            'days': DoctorSchedules.DAY_CHOICES,
            'section': 'schedule_timings'
        }
        
        return render(request, 'frontend/dashboard/hospitals/sections/schedule-timings.html', context)

    except Hospital.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'لا يمكنك الوصول إلى هذه الصفحة'
        })
    except Exception as e:
        print(f"Error in schedule_timings: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'حدث خطأ أثناء معالجة الطلب'
        })

@login_required(login_url='/user/login')

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

@login_required(login_url='/user/login')

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
        invoices = invoices.filter(payment_status_id=payment_status)
    payment_method= request.GET.get('payment_method')
    if payment_method:
        invoices= invoices.filter(payment_method__id=payment_method)
        
    patient_name = request.GET.get('patient_name')
    if patient_name:
        invoices = invoices.filter(booking__patient__full_name__icontains=patient_name)
    amount_min = request.GET.get('amount_min')
    if amount_min:
        invoices = invoices.filter(payment_totalamount__gte=amount_min)
        
    amount_max = request.GET.get('amount_max')
    if amount_max:
        invoices = invoices.filter(payment_totalamount__lte=amount_max)

    # تحديث الإحصائيات بعد التصفية
    context.update({
        'invoices': invoices.order_by('-payment_date'),
        'payment_statuses': Payment.PaymentStatus_choices
    })
    
    return render(request, 'frontend/dashboard/hospitals/sections/invoice_table.html', context)

@login_required(login_url='/user/login')

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
def update_hospital_profile(request):
    """معالجة طلب تعديل بيانات ملف المستشفى الشخصي"""
    if request.method == 'POST':
        try:
            hospital = get_object_or_404(Hospital, hospital_manager=request.user)
            print(request.POST)  
            # Collect the updated data from the form
            name = request.POST.get('hospital_name')
            location = request.POST.get('hospital_location')
            description = request.POST.get('description')
            about = request.POST.get('about')
            photo = request.FILES.get('photo')
            
            # Create the update request object
            update_request = HospitalUpdateRequest(
                hospital=hospital,
                name=name if name != hospital.name else None,
                location=location if location != hospital.location else None,
                description=description if description != hospital.description else None,
                about=about if about != hospital.about else None,
                photo=photo if photo else None,
                created_by=request.user
            )
            update_request.save()

            messages.success(request, 'تم إرسال طلب تعديل البيانات بنجاح. سيتم مراجعته من قبل المسؤول.')
            return redirect('hospitals:index')
           

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء معالجة طلب التعديل: {e}.')
            return redirect('hospitals:index')

    return redirect('hospitals:index')

@login_required(login_url='/user/login')
def get_doctor(request, doctor_id):
    try:
        print(f"Getting doctor {doctor_id}")
        hospital = get_object_or_404(Hospital, user=request.user)  # تعديل هنا
        print(f"Found hospital: {hospital.id}")
        
        doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
        print(f"Found doctor: {doctor.full_name}")
        
        # Get current price
        price = DoctorPricing.objects.filter(
            doctor=doctor,
            hospital=hospital
        ).first()
        print(f"Current price: {price.amount if price else 'None'}")
        
        response_data = {
            'status': 'success',
            'doctor': {
                'id': doctor.id,
                'full_name': doctor.full_name,
                'specialty': doctor.specialty_id,
                'email': doctor.email,
                'phone_number': doctor.phone_number,
                'gender': doctor.gender,
                'experience_years': doctor.experience_years,
                'price': str(price.amount) if price else '',
                'status': doctor.status,
                'about': doctor.about or '',
                'photo_url': doctor.photo.url if doctor.photo else None
            }
        }
        print(f"Returning data: {response_data}")
        return JsonResponse(response_data)
        
    except Hospital.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على المستشفى'
        }, status=404)
    except Doctor.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على الطبيب'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@login_required(login_url='/user/login')
@csrf_exempt
def update_doctor(request, doctor_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')
    
    try:
        print("="*50)
        print(f"Updating doctor {doctor_id}")
        print(f"POST data: {request.POST}")
        
        # Get hospital and doctor
        hospital = get_object_or_404(Hospital, user=request.user)  # تعديل هنا
        doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
        
        # Update doctor information
        doctor.full_name = request.POST.get('full_name')
        doctor.specialty_id = request.POST.get('specialty')
        doctor.email = request.POST.get('email')
        doctor.phone_number = request.POST.get('phone_number')
        doctor.gender = request.POST.get('gender')
        doctor.experience_years = request.POST.get('experience_years')
        doctor.status = request.POST.get('status') == '1'
        doctor.about = request.POST.get('about', '')
        
        # Handle photo upload
        if 'photo' in request.FILES:
            doctor.photo = request.FILES['photo']
        
        doctor.save()
        
        # Update doctor price
        price = DoctorPricing.objects.filter(doctor=doctor, hospital=hospital).first()
        new_price = request.POST.get('price')
        
        if new_price:
            if price:
                # Create price history record
                DoctorPricingHistory.objects.create(
                    doctor=doctor,
                    hospital=hospital,
                    amount=new_price,
                    previous_amount=price.amount
                )
                # Update current price
                price.amount = new_price
                price.save()
            else:
                # Create new price record
                DoctorPricing.objects.create(
                    doctor=doctor,
                    hospital=hospital,
                    amount=new_price
                )
        
        return JsonResponse({
            'status': 'success',
            'message': 'تم تحديث بيانات الطبيب بنجاح'
        })
        
    except Hospital.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على المستشفى'
        }, status=404)
    except Doctor.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على الطبيب'
        }, status=404)
    except Exception as e:
        print(f"Error updating doctor: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@login_required(login_url='/user/login')
def delete_doctor(request, doctor_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')
    
    try:
        # Get hospital and doctor
        hospital = get_object_or_404(Hospital, user=request.user)
        doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
        
        # Remove the doctor from this hospital
        doctor.hospitals.remove(hospital)
        
        # Delete the doctor's pricing for this hospital
        DoctorPricing.objects.filter(doctor=doctor, hospital=hospital).delete()
        
        # If the doctor is not associated with any other hospitals, delete the doctor
        if doctor.hospitals.count() == 0:
            doctor.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'تم حذف الطبيب بنجاح'
        })
        
    except Doctor.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على الطبيب'
        }, status=404)
    except Exception as e:
        print(f"Error deleting doctor: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@login_required(login_url='/user/login')
def get_doctor_history(request, doctor_id):
    try:
        hospital = get_object_or_404(Hospital, user=request.user)  # تعديل هنا
        doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
        
        # جلب سجل أسعار الطبيب
        history = DoctorPricingHistory.objects.filter(
            doctor=doctor,
            hospital=hospital
        ).order_by('-change_date')
        
        # الحصول على السعر الحالي
        current_price = DoctorPricing.objects.filter(
            doctor=doctor,
            hospital=hospital
        ).first()
        
        history_data = []
        for entry in history:
            history_data.append({
                'date': entry.change_date.strftime('%Y-%m-%d %H:%M'),
                'amount': str(entry.amount),
                'previous_amount': str(entry.previous_amount) if entry.previous_amount else None,
            })
        
        return JsonResponse({
            'status': 'success',
            'doctor': {
                'id': doctor.id,
                'full_name': doctor.full_name,
                'current_price': str(current_price.amount) if current_price else None,
            },
            'history': history_data
        })
        
    except Hospital.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على المستشفى'
        }, status=404)
    except Doctor.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على الطبيب'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@login_required(login_url='/user/login')
def add_doctor_form(request):
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)
    speciality = Specialty.objects.filter(status=True)
    context = {
        'hospital': hospital,
        'speciality': speciality,
    }
    return render(request, 'frontend/dashboard/hospitals/page/add_doctor.html', context)

@login_required(login_url='/user/login')
def doctor_details(request, doctor_id):
    try:
        print(f"Accessing doctor details for ID: {doctor_id}")  # Debug print
        hospital = get_object_or_404(Hospital, user=request.user)
        doctor = get_object_or_404(Doctor.objects.select_related('specialty'), id=doctor_id, hospitals=hospital)
        
        # Get current price
        doctor_price = DoctorPricing.objects.filter(
            doctor=doctor,
            hospital=hospital
        ).first()
        
        context = {
            'doctor': doctor,
            'doctor_price': doctor_price,
            'section': 'doctors'  # For active menu highlighting
        }
        
        print(f"Rendering template with context: {context}")  # Debug print
        return render(request, 'frontend/dashboard/hospitals/page/doctor_details.html', context)
        
    except Doctor.DoesNotExist:
        messages.error(request, 'لم يتم العثور على الطبيب')
        return redirect('hospitals:index')
    except Exception as e:
        print(f"Error in doctor_details view: {str(e)}")  # Debug print
        messages.error(request, str(e))
        return redirect('hospitals:index')