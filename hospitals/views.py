from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, date, time
import traceback
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

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('home:home')

User = get_user_model()

@login_required(login_url='/user/login')
def index(request):
    user = request.user

    # التحقق من نوع المستخدم
    if user.user_type == 'hospital_manager':
        # إذا كان المستخدم مدير مستشفى
        hospital = get_object_or_404(Hospital, user=user)
        staff_obj = None
    elif user.user_type == 'hospital_staff':
        # إذا كان المستخدم موظف مستشفى
        try:
            # استيراد نموذج الموظف
            from hospital_staff.models import HospitalStaff
            staff_obj = get_object_or_404(HospitalStaff, user=user)
            hospital = staff_obj.hospital
        except Exception as e:
            print(f"\n\nخطأ في الحصول على معلومات الموظف: {str(e)}\n\n")
            messages.error(request, "حدث خطأ في الحصول على معلومات الموظف. يرجى التواصل مع مدير النظام.")
            return redirect('users:logout')
    else:
        # إذا كان نوع المستخدم غير مدعوم
        messages.error(request, "ليس لديك صلاحية الوصول إلى هذه الصفحة.")
        return redirect('users:logout')

    speciality = Specialty.objects.filter(status=True)
    payment_method = HospitalPaymentMethod.objects.filter(hospital=hospital)
    bookings = Booking.objects.filter(hospital=hospital)
    doctors = Doctor.objects.filter(hospitals=hospital).select_related('specialty').prefetch_related(
        Prefetch('pricing', queryset=DoctorPricing.objects.filter(hospital=hospital))
    )
    phoneNumber = PhoneNumber.objects.filter(hospital=hospital)
    city = City.objects.filter(status=True)
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

    # Get hospital location from HospitalUpdateRequest
    hospital_location = None
    try:
        update_request = HospitalUpdateRequest.objects.filter(hospital=hospital, status='approved').first()
        if update_request and update_request.location:
            hospital_location = update_request.location
            print(f"Found hospital location: {hospital_location}")
    except Exception as e:
        print(f"Error getting hospital location: {str(e)}")

    # Importar el modelo Advertisement si aún no está importado
    try:
        from advertisements.models import Advertisement
        # Obtener anuncios para este hospital
        advertisements = Advertisement.objects.filter(hospital=hospital)
    except ImportError:
        # Si el modelo no está disponible, usar una lista vacía
        advertisements = []
    except Exception as e:
        # Si hay otro error, registrarlo y usar una lista vacía
        print(f"Error al cargar anuncios: {str(e)}")
        advertisements = []

    # التحقق مما إذا كان الطلب يطلب بيانات الحجوزات بتنسيق JSON
    if request.GET.get('format') == 'json' and request.GET.get('section') == 'appointments':
        # تحضير بيانات الحجوزات للاستجابة JSON
        bookings_data = []
        for booking in bookings:
            booking_data = {
                'id': booking.id,
                'patient_name': booking.patient.user.get_full_name() if booking.patient and booking.patient.user else 'غير معروف',
                'patient_phone': booking.patient.user.mobile_number if booking.patient and booking.patient.user else '',
                'patient_image': booking.patient.user.profile_picture.url if booking.patient and booking.patient.user and booking.patient.user.profile_picture else None,
                'doctor_name': booking.doctor.full_name if booking.doctor else 'غير معروف',
                'doctor_specialty': booking.doctor.specialty.name if booking.doctor and booking.doctor.specialty else '',
                'doctor_image': booking.doctor.photo.url if booking.doctor and booking.doctor.photo else None,
                'booking_date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else '',
                'booking_time': booking.booking_time.strftime('%H:%M') if booking.booking_time else '',
                'amount': booking.amount,
                'status': booking.status,
                'payment_status': 'مدفوع' if booking.payment_status == 'paid' else 'غير مدفوع',
            }
            bookings_data.append(booking_data)
        
        # إرجاع استجابة JSON
        return JsonResponse({
            'bookings': bookings_data,
            'total_bookings': bookings.count(),
            'confirmed_bookings': bookings.filter(status='confirmed').count(),
            'pending_bookings': bookings.filter(status='pending').count(),
            'completed_bookings': bookings.filter(status='completed').count(),
        })
    
    context = {
        "payment_options": PaymentOption.objects.filter(is_active=True),
        "payment_methods": payment_method,
        'hospital': hospital,
        'users': User.objects.all(),
        'bookings': bookings,
        'city': city,
        'cities': City.objects.filter(status=True),  # Add all active cities for dropdown
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
        'staff_obj': staff_obj,  # إضافة معلومات الموظف إلى السياق
        'advertisements': advertisements,  # Añadir anuncios al contexto
    }



    return render(request, 'frontend/dashboard/hospitals/index.html', context)


@login_required(login_url='/user/login')

def blog_list(request):
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)
    # Use prefetch_related to efficiently load comments and their users
    posts = Post.objects.filter(author=hospital).prefetch_related('comments__user')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'allBlogs': page_obj,
    }
    return render(request, 'frontend/dashboard/hospitals/sections/hospital_blogs.html', context)


@login_required(login_url='/user/login')
def blog_list_json(request):
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)
    posts = Post.objects.filter(author=hospital, status=True)

    blogs_data = []
    for post in posts:
        blog_data = {
            'id': post.id,
            'title': post.title,
            'content_preview': post.content[:100] + '...' if len(post.content) > 100 else post.content,
            'image_url': post.image.url if post.image else '',
            'author_name': hospital.name,
            'created_at': post.created_at.strftime('%Y-%m-%d'),
            'status': post.status
        }
        blogs_data.append(blog_data)

    return JsonResponse({'status': 'success', 'blogs': blogs_data})

@login_required(login_url='/user/login')

def blog_pending_list(request):
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)
    # Use prefetch_related to efficiently load comments and their users
    posts = Post.objects.filter(author=hospital).prefetch_related('comments__user')
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
    hospital = get_object_or_404(Hospital, user=user)

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
    hospital = get_object_or_404(Hospital, user=user)
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


@login_required(login_url='/user/login')
def blog_detail(request, blog_id):
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)
    blog = get_object_or_404(Post, id=blog_id, author=hospital)

    # استخدام prefetch_related لتحميل التعليقات ومستخدميها بكفاءة
    blog = Post.objects.prefetch_related('comments__user').get(id=blog_id, author=hospital)

    # ترتيب التعليقات من الأحدث إلى الأقدم
    comments = blog.comments.all().order_by('-created_at')

    context = {
        'blog': blog,
        'comments': comments,
    }
    return render(request, 'frontend/dashboard/hospitals/sections/hospitals-blog-detail.html', context)




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

def add_blog(request):
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

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
    hospital = get_object_or_404(Hospital, user=user)
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




    """عرض تفاصيل المستشفى للزوار"""
    try:
        hospital = get_object_or_404(Hospital, slug=slug)

        # طباعة معلومات تصحيح
        print(f"Found hospital: {hospital.name}, Status: {hospital.status}")

        # الحصول على الأطباء المرتبطين بالمستشفى
        doctors = Doctor.objects.filter(hospitals=hospital, status=True).select_related('specialty')
        print(f"Found {doctors.count()} doctors")

        # الحصول على التخصصات المتاحة في المستشفى
        specialties = Specialty.objects.filter(doctor__hospitals=hospital).distinct()
        print(f"Found {specialties.count()} specialties")

        # إحصائيات المستشفى
        stats = {
            'doctors_count': doctors.count(),
            'specialties_count': specialties.count(),
        }

        context = {
            'hospital': hospital,
            'doctors': doctors,
            'specialties': specialties,
            'stats': stats,
        }

        # طباعة معلومات تصحيح
        print(f"Rendering template: frontend/home/pages/hospital_detail.html")
        print(f"Context: {context}")

        # تجربة استخدام قالب بديل
        return render(request, 'frontend/home/pages/hospital_detail.html', context)
    except Exception as e:
        print(f"Error in hospital_detail: {str(e)}")
        # إعادة توجيه المستخدم إلى الصفحة الرئيسية في حالة حدوث خطأ
        return redirect('home:home')

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
    # طباعة رسالة تأكيد للتحقق من وصول الطلب إلى هذه الوظيفة
    print("\n\n*** تم الوصول إلى صفحة نجاح تقديم الطلب ***\n\n")
    print(f"\n\n*** المسار المطلوب: {request.path} ***\n\n")
    print(f"\n\n*** المستخدم مسجل الدخول: {request.user.is_authenticated} ***\n\n")
    return render(request, 'frontend/auth/hospital-request-success.html')

def hospital_request_status(request, request_id):
    """عرض حالة الطلب"""
    hospital_request = get_object_or_404(HospitalAccountRequest, id=request_id)
    return render(request, 'frontend/auth/hospital-request-status.html', {
        'request': hospital_request
    })




@login_required(login_url='/user/login')

def filter_doctors(request):
    hospital = get_object_or_404(Hospital, user=request.user)

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


@login_required(login_url='/user/login')
def add_payment_method(request):
    # Get the hospital associated with the logged-in user
    try:
        if request.user.user_type == 'hospital_manager':
            hospital = get_object_or_404(Hospital, user=request.user)
        elif request.user.user_type == 'hospital_staff':
            from hospital_staff.models import HospitalStaff
            staff_obj = get_object_or_404(HospitalStaff, user=request.user)
            hospital = staff_obj.hospital
        else:
            messages.error(request, "ليس لديك صلاحية للقيام بهذه العملية")
            return redirect('hospitals:index')
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء تحديد المستشفى: {str(e)}")
        return redirect('hospitals:index')
    
    if request.method == "POST":
        payment_option_id = request.POST.get("payment_option")
        account_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        iban = request.POST.get("iban")
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "1"

        if not all([payment_option_id, account_name, account_number, iban, description]):
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة")
            return redirect('hospitals:index')

        try:
            payment_option = PaymentOption.objects.get(id=payment_option_id)
            
            # Check if this payment option already exists for this hospital
            existing_payment = HospitalPaymentMethod.objects.filter(
                hospital=hospital,
                payment_option=payment_option
            ).first()
            
            if existing_payment:
                # Update the existing payment method instead of creating a new one
                existing_payment.account_name = account_name
                existing_payment.account_number = account_number
                existing_payment.iban = iban
                existing_payment.description = description
                existing_payment.is_active = is_active
                existing_payment.save()
                messages.success(request, "تم تحديث طريقة الدفع بنجاح")
            else:
                # Create a new payment method
                HospitalPaymentMethod.objects.create(
                    hospital=hospital,
                    payment_option=payment_option,
                    account_name=account_name,
                    account_number=account_number,
                    iban=iban,
                    description=description,
                    is_active=is_active,
                )
                messages.success(request, "تمت إضافة طريقة الدفع بنجاح")
        except PaymentOption.DoesNotExist:
            messages.error(request, "خيار الدفع غير موجود")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء إضافة طريقة الدفع: {str(e)}")


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



from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
@require_POST
@csrf_exempt
def accept_appointment(request, booking_id):
    """قبول الحجز مع إرجاع رد JSON مناسب لرسالة الـ Toast"""
    if not hasattr(request.user, 'hospital'):
        return JsonResponse({
            'status': 'error',
            'message': 'ليس لديك صلاحية للقيام بهذا الإجراء',
            'toast_class': 'bg-danger'
        }, status=403)

    try:
        booking = get_object_or_404(Booking, id=booking_id)
        payment = get_object_or_404(Payment, booking=booking)

        if booking.hospital != request.user.hospital:
            return JsonResponse({
                'status': 'error',
                'message': 'ليس لديك صلاحية للقيام بهذا الإجراء',
                'toast_class': 'bg-danger'
            }, status=403)

        # تحديث البيانات
        doctor_shifts = booking.appointment_time
        if doctor_shifts:
            doctor_shifts.booked_slots += 1
            doctor_shifts.save()

        booking.status = 'confirmed'
        booking.payment_verified = True
        booking.payment_verified_at = timezone.now()
        booking.payment_verified_by = request.user
        booking.save()

        BookingStatusHistory.objects.create(
            booking=booking,
            status='confirmed',
            created_by=request.user,
            notes='تم قبول الحجز من قبل المستشفى'
        )

        payment.payment_status = 2
        payment.save()

        return JsonResponse({
            'status': 'success',
            'message': 'تم قبول الحجز بنجاح',
            'toast_class': 'bg-success',
            'booking_status': 'confirmed'
        })

    except (Booking.DoesNotExist, Payment.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'الحجز غير موجود',
            'toast_class': 'bg-danger'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'حدث خطأ: {str(e)}',
            'toast_class': 'bg-danger'
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


def cancel_appointment(request, booking_id):
    """إلغاء الحجز"""
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

        # تحديث حالة الحجز إلى ملغى
        booking.status = 'cancelled'
        booking.save()

        # تنقيص عدد الحجوزات في الفترة المحددة
        doctor_shifts = booking.appointment_time
        if doctor_shifts:
            doctor_shifts.booked_slots -= 1
            doctor_shifts.save()

        # إنشاء سجل جديد لحالة الحجز
        BookingStatusHistory.objects.create(
            booking=booking,
            status='cancelled',
            created_by=request.user,
            notes='تم إلغاء الحجز'
        )

        return JsonResponse({
            'status': 'success',
            'message': 'تم إلغاء الحجز بنجاح',
            'toast_class': 'bg-success'
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
            'message': str(e),
            'toast_class': 'bg-danger'
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
            'patient_name':  f"{booking.patient.user.first_name} {booking.patient.user.last_name}",
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
                    'patient_name': f"{booking.patient.user.first_name} {booking.patient.user.last_name}",
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


from django.core.exceptions import ObjectDoesNotExist

@login_required(login_url='/user/login')
def schedule_timings(request):
    import json
    from django.views.decorators.http import require_http_methods

    try:
        print(f"User ID: {request.user.id}")
        print(f"User Type: {request.user.user_type}")
        print(f"Request method: {request.method}")

        # التحقق من نوع المستخدم
        if request.user.user_type == 'hospital_manager':
            # إذا كان المستخدم مدير مستشفى
            hospital = get_object_or_404(Hospital, user=request.user)
        elif request.user.user_type == 'hospital_staff':
            # إذا كان المستخدم موظف مستشفى
            from hospital_staff.models import HospitalStaff
            staff = get_object_or_404(HospitalStaff, user=request.user)
            hospital = staff.hospital

            # التحقق من صلاحية الموظف لإدارة المواعيد
            from hospital_staff.permissions import check_permission
            if not check_permission(request.user, 'manage_appointments'):
                print(f"Staff does not have permission to manage appointments: {request.user.id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'ليس لديك صلاحية لإدارة المواعيد'
                })
        else:
            # إذا كان نوع المستخدم غير مدعوم
            print(f"Invalid user type: {request.user.user_type}")
            return JsonResponse({
                'status': 'error',
                'message': 'لا يمكنك الوصول إلى هذه الصفحة'
            })
        print(f"Found hospital: {hospital.name}")
        print(f"Found hospital for user {request.user.id}: {hospital.id}")

        # Handle DELETE request for shift deletion
        if request.method == 'DELETE':
            try:
                data = json.loads(request.body)
                shift_id = data.get('shift_id')

                if not shift_id:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'معرف الموعد مطلوب'
                    })

                try:
                    shift = DoctorShifts.objects.get(id=shift_id)

                    # Check if the shift belongs to this hospital
                    if shift.hospital.id != hospital.id:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'لا يمكنك حذف هذا الموعد'
                        })

                    # Check if there are any booked appointments
                    if shift.booked_slots > 0:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'لا يمكن حذف الموعد لأنه يحتوي على حجوزات'
                        })

                    # Delete the shift
                    shift.delete()

                    return JsonResponse({
                        'status': 'success',
                        'message': 'تم حذف الموعد بنجاح'
                    })

                except DoctorShifts.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'الموعد غير موجود'
                    })

            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'بيانات غير صالحة'
                })

        # Handle PUT request for shift updates
        elif request.method == 'POST' and request.POST.get('_method') == 'PUT':
            try:
                print('Received edit request with data:', request.POST)
                shift_id = request.POST.get('shift_id')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                max_appointments = request.POST.get('max_appointments')

                print(f'Parsed data: shift_id={shift_id}, start_time={start_time}, end_time={end_time}, max_appointments={max_appointments}')

                if not all([shift_id, start_time, end_time, max_appointments]):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'جميع الحقول مطلوبة'
                    })

                try:
                    shift = DoctorShifts.objects.get(id=shift_id)

                    # Check if the shift belongs to this hospital
                    if shift.hospital.id != hospital.id:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'لا يمكنك تعديل هذا الموعد'
                        })

                    # Validate time format and order
                    try:
                        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                        end_time_obj = datetime.strptime(end_time, '%H:%M').time()

                        if start_time_obj >= end_time_obj:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'وقت البداية يجب أن يكون قبل وقت النهاية'
                            })
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'صيغة الوقت غير صحيحة'
                        })

                    # Update the shift
                    shift.start_time = start_time_obj
                    shift.end_time = end_time_obj
                    shift.available_slots = int(max_appointments)

                    # Update day if provided
                    day = request.POST.get('day')
                    if day:
                        try:
                            day_int = int(day)
                            if 0 <= day_int <= 6:  # تحقق من أن القيمة بين 0 و 6
                                # تحديث الجدول الزمني للطبيب
                                schedule = shift.doctor_schedule
                                schedule.day = day_int
                                schedule.save()
                            else:
                                return JsonResponse({
                                    'status': 'error',
                                    'message': 'قيمة اليوم غير صالحة'
                                })
                        except ValueError:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'قيمة اليوم يجب أن تكون رقماً'
                            })

                    shift.save()
                    print(f'Successfully updated shift {shift.id}. New day: {shift.doctor_schedule.day}')

                    print('Successfully updated shift:', shift.id)

                    return JsonResponse({
                        'status': 'success',
                        'message': 'تم تحديث الموعد بنجاح'
                    })

                except DoctorShifts.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'الموعد غير موجود'
                    })

            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'بيانات غير صالحة'
                })

        elif request.method == 'POST':
            print("Received POST request for schedule_timings")
            try:
                doctor_id = request.POST.get('doctor_id')
                day = request.POST.get('day')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                max_appointments = int(request.POST.get('max_appointments', 1))

                print(f"Received data: doctor_id={doctor_id}, day={day}, start_time={start_time}, end_time={end_time}, max_appointments={max_appointments}")

                if not all([doctor_id, day, start_time, end_time]):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'جميع الحقول مطلوبة'
                    })

                # Get the doctor
                try:
                    doctor = Doctor.objects.get(id=doctor_id)
                    print(f"Found doctor: {doctor.id} - {doctor.full_name}")
                except Doctor.DoesNotExist:
                    print(f"Doctor not found with id: {doctor_id}")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'الطبيب غير موجود'
                    })

                # Check if the doctor belongs to this hospital
                if not doctor.hospitals.filter(id=hospital.id).exists():
                    print(f"Doctor {doctor.id} does not belong to hospital {hospital.id}")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'هذا الطبيب لا ينتمي إلى مستشفاك'
                    })

                # Validate time format and order
                try:
                    start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                    end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                    print(f"Time validation: start={start_time_obj}, end={end_time_obj}")

                    if start_time_obj >= end_time_obj:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'وقت البداية يجب أن يكون قبل وقت النهاية'
                        })
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'صيغة الوقت غير صحيحة'
                    })

                # التحقق من عدم وجود تعارض في مواعيد الطبيب بين المستشفيات المختلفة
                # البحث عن جميع مواعيد الطبيب في نفس اليوم في جميع المستشفيات الأخرى
                conflicting_schedules = DoctorSchedules.objects.filter(
                    doctor=doctor,
                    day=day
                ).exclude(hospital=hospital)

                # التحقق من كل جدول للتأكد من عدم وجود تداخل في الأوقات
                for schedule in conflicting_schedules:
                    conflicting_shifts = DoctorShifts.objects.filter(
                        doctor_schedule=schedule,
                        start_time__lt=end_time_obj,
                        end_time__gt=start_time_obj
                    )

                    if conflicting_shifts.exists():
                        conflicting_shift = conflicting_shifts.first()
                        hospital_name = conflicting_shift.hospital.name
                        shift_time = f"{conflicting_shift.start_time.strftime('%H:%M')} - {conflicting_shift.end_time.strftime('%H:%M')}"
                        return JsonResponse({
                            'status': 'error',
                            'message': f'يوجد تعارض في المواعيد: الطبيب لديه موعد في مستشفى {hospital_name} في نفس اليوم من الساعة {shift_time}'
                        })

                # Get or create the schedule for this doctor and day
                schedule, created = DoctorSchedules.objects.get_or_create(
                    doctor=doctor,
                    hospital=hospital,
                    day=day
                )
                print(f"{'Created new' if created else 'Using existing'} schedule: {schedule.id}")

                # Create or update the shift
                shift = DoctorShifts.objects.create(
                    doctor_schedule=schedule,
                    hospital=hospital,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    available_slots=max_appointments,
                    booked_slots=0
                )

                print(f"{'Created' if created else 'Updated'} schedule {schedule.id} with shift {shift.id}")

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
                print(f"Error: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
            except Exception as e:
                print(f"Error adding schedule: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                print(f"Error traceback: {traceback.format_exc()}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'حدث خطأ أثناء إضافة الموعد'
                })

        # GET request - تم التعديل هنا
        doctors = Doctor.objects.filter(hospitals=hospital)
        doctor_id = request.GET.get('doctor_id')

        if doctor_id:
            print(f"Looking for doctor ID: {doctor_id}")
            try:
                # Verify the doctor belongs to this hospital
                doctor = Doctor.objects.get(id=doctor_id)
                print(f"Found doctor: {doctor.id} - {doctor.full_name}")

                # Check if doctor belongs to hospital
                if not doctor.hospitals.filter(id=hospital.id).exists():
                    print(f"Doctor {doctor.id} does not belong to hospital {hospital.id}")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'الطبيب غير موجود في هذا المستشفى'
                    })

                print(f"Doctor {doctor.id} belongs to hospital {hospital.id}")

                # Get the doctor's schedules with shifts
                schedules = DoctorSchedules.objects.filter(
                    doctor_id=doctor_id,
                    hospital=hospital
                ).prefetch_related('shifts')

                print(f"Found {schedules.count()} schedules for doctor {doctor_id}")

                schedules_data = {}
                for schedule in schedules:
                    shifts = schedule.shifts.all()
                    print(f"Found {shifts.count()} shifts for schedule {schedule.id} on day {schedule.day}")

                    if shifts.exists():
                        if schedule.day not in schedules_data:
                            schedules_data[schedule.day] = []

                        for shift in shifts:
                            schedules_data[schedule.day].append({
                                'id': shift.id,
                                'start_time': shift.start_time.strftime('%H:%M'),
                                'end_time': shift.end_time.strftime('%H:%M'),
                                'available_slots': shift.available_slots,
                                'booked_slots': shift.booked_slots
                            })

                return JsonResponse({
                    'status': 'success',
                    'doctor_schedules': schedules_data
                })
            except Doctor.DoesNotExist:
                print(f"Doctor {doctor_id} not found")
                return JsonResponse({
                    'status': 'error',
                    'message': 'الطبيب غير موجود'
                })

            # هذا الكود غير مطلوب لأنه تم بالفعل إرجاع الاستجابة في الأعلى

        context = {
            'doctors': doctors,
            'days': DoctorSchedules.DAY_CHOICES,
            'section': 'schedule_timings'
        }

        return render(request, 'frontend/dashboard/hospitals/sections/schedule-timings.html', context)

    except Hospital.DoesNotExist:
        print(f"Hospital not found for user {request.user.id}")
        return JsonResponse({
            'status': 'error',
            'message': 'لا يمكنك الوصول إلى هذه الصفحة'
        })
    except Doctor.DoesNotExist:
        print(f"Doctor {doctor_id} not found in hospital {hospital.id}")
        return JsonResponse({
            'status': 'error',
            'message': 'الطبيب غير موجود في هذا المستشفى'
        })
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
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
            print(f"Error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'حدث خطأ أثناء حذف الموعد'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'طريقة الطلب غير صحيحة'
    }, status=405)


from django.shortcuts import render, redirect, get_object_or_404
from doctors.models import Doctor
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Hospital

def all_hospitals(request):
    search_query = request.GET.get('search', '')
    hospitals = Hospital.objects.filter(status=True)

    if search_query:
        hospitals = hospitals.filter(name__icontains=search_query)

    hospitals = hospitals.annotate(
        doctors_count=models.Count('doctors', distinct=True),
        specialties_count=models.Count('doctors__specialty', distinct=True)
    )

    # Pagination
    paginator = Paginator(hospitals, 6)  # Show 6 hospitals per page
    page = request.GET.get('page')

    try:
        hospitals = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        hospitals = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        hospitals = paginator.page(paginator.num_pages)

    return render(request, 'frontend/hospitals/all_hospitals.html', {
        'hospitals': hospitals,
        'title': 'المستشفيات',
        'search_query': search_query
    })

def hospital_details(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)

    # Get doctors with their ratings
    doctors = hospital.doctors.select_related('specialty').all()

    # Ensure all doctors have slugs
    from django.utils.text import slugify
    updated_doctors = []
    for doctor in doctors:
        # Print debug info
        print(f"Processing doctor: {doctor.full_name}, Current slug: {doctor.slug}")

        # Always generate a new slug if it's empty or invalid
        if not doctor.slug or not doctor.slug.strip():
            base_slug = slugify(doctor.full_name)
            if not base_slug:  # If name doesn't generate valid slug
                base_slug = f'doctor-{doctor.id}'

            # Handle slug duplication
            unique_slug = base_slug
            counter = 1
            while Doctor.objects.filter(slug=unique_slug).exclude(pk=doctor.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            # Update the doctor's slug
            doctor.slug = unique_slug
            doctor.save(update_fields=['slug'])
            print(f"Updated slug for {doctor.full_name} to: {doctor.slug}")

        updated_doctors.append(doctor)

    # Now get the doctors again with annotations
    doctors = hospital.doctors.select_related('specialty').annotate(
        rating=models.Avg('reviews__rating'),
        reviews_count=models.Count('reviews')
    ).all()

    # Get unique specialties count
    specialties_count = doctors.values('specialty').distinct().count()

    # Final verification
    for doctor in doctors:
        print(f"Final verification - Doctor: {doctor.full_name}, Slug: {doctor.slug}")
        if not doctor.slug:
            print(f"WARNING: Doctor {doctor.full_name} still has no slug!")

    context = {
        'hospital': hospital,
        'doctors': doctors,
        'doctors_count': doctors.count(),
        'specialties_count': specialties_count,
        'title': hospital.name
    }

    return render(request, 'frontend/hospitals/hospital_details.html', context)

@login_required(login_url='/user/login')
def invoice_view(request, payment_id):
    # الحصول على الفاتورة المحددة
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'frontend/dashboard/hospitals/invoice_detail.html', {'payment': payment})



@login_required(login_url='/user/login')
def filter_invoices(request):
    """تصفية الفواتير"""
    hospital = request.user.hospital
    invoices = Payment.objects.filter(payment_method__hospital=hospital)

    # Get payment methods available for this hospital
    payment_methods = HospitalPaymentMethod.objects.filter(
        hospital=hospital,
        is_active=True
    ).select_related('payment_option')

    # Apply filters
    date_from = request.GET.get('date_from')
    if date_from:
        invoices = invoices.filter(payment_date__date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        invoices = invoices.filter(payment_date__date__lte=date_to)

    payment_status = request.GET.get('payment_status')
    if payment_status:
        invoices = invoices.filter(payment_status=payment_status)

    payment_method = request.GET.get('payment_method')
    if payment_method:
        invoices = invoices.filter(payment_method__id=payment_method)

    patient_name = request.GET.get('patient_name')
    if patient_name:
        invoices = invoices.filter(booking__patient__user__full_name__icontains=patient_name)

    amount_min = request.GET.get('amount_min')
    if amount_min:
        invoices = invoices.filter(payment_totalamount__gte=amount_min)

    amount_max = request.GET.get('amount_max')
    if amount_max:
        invoices = invoices.filter(payment_totalamount__lte=amount_max)

    # For AJAX requests
    # For AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        invoices_data = []
        for invoice in invoices:
            invoices_data.append({
                'id': invoice.id,
                'patient_name': invoice.booking.patient.user.get_full_name(),
                'doctor_name': invoice.booking.doctor.full_name if invoice.booking.doctor else '',
                'amount': str(invoice.payment_totalamount),
                'status': invoice.get_status_display(),
                'date': invoice.payment_date.strftime("%d %b %Y"),
                'method': invoice.payment_method.payment_option.method_name,
                'status_code': invoice.payment_status,
                'patient_photo': invoice.booking.patient.user.profile_picture.url if invoice.booking.patient.user.profile_picture else '/static/path/to/default/image.jpg',
                'doctor_photo': invoice.booking.doctor.photo.url if invoice.booking.doctor.photo else '/static/path/to/default/image.jpg',
            })
        return JsonResponse({'invoices': invoices_data})

    context = {
        'invoices': invoices.order_by('-payment_date'),
        'payment_statuses': Payment.PaymentStatus_choices,
        'payment_methods': payment_methods,
        'request': request,
    }

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
    print("\n\n*** update_hospital_profile view called ***\n\n")
    print(f"Request method: {request.method}")
    print(f"User type: {request.user.user_type}")

    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")

        try:
            # Get the hospital based on user type
            hospital = None
            if request.user.user_type == 'hospital_manager':
                hospital = Hospital.objects.get(user=request.user)
                print(f"Found hospital for manager: {hospital.name} (ID: {hospital.id})")
            elif request.user.user_type == 'hospital_staff':
                # Import here to avoid circular imports
                from hospital_staff.models import HospitalStaff
                staff = HospitalStaff.objects.get(user=request.user)
                hospital = staff.hospital
                print(f"Found hospital for staff: {hospital.name} (ID: {hospital.id})")

            # Update user's information (mobile number, username, email, profile picture, city, state)
            mobile_number = request.POST.get('mobile_number')
            username = request.POST.get('username')
            email = request.POST.get('email')
            user_city = request.POST.get('user_city')
            user_state = request.POST.get('user_state')
            profile_picture = request.FILES.get('profile_picture')

            user_updated = False

            # Check if username is being changed and is not already taken
            if username and username != request.user.username:
                if CustomUser.objects.filter(username=username).exclude(id=request.user.id).exists():
                    messages.error(request, 'اسم المستخدم مستخدم بالفعل. يرجى اختيار اسم مستخدم آخر.')
                    return redirect('/hospital/?section=doctor_profile_settings')
                request.user.username = username
                user_updated = True
                print(f"Updated username to: {username}")

            # Check if email is being changed and is not already taken
            if email and email != request.user.email:
                if CustomUser.objects.filter(email=email).exclude(id=request.user.id).exists():
                    messages.error(request, 'البريد الإلكتروني مستخدم بالفعل. يرجى اختيار بريد إلكتروني آخر.')
                    return redirect('/hospital/?section=doctor_profile_settings')
                request.user.email = email
                user_updated = True
                print(f"Updated email to: {email}")

            if mobile_number:
                request.user.mobile_number = mobile_number
                user_updated = True
                print(f"Updated user mobile number to: {mobile_number}")

            # Update user city and state
            if user_city is not None:
                request.user.city = user_city
                user_updated = True
                print(f"Updated user city to: {user_city}")

            if user_state is not None:
                request.user.state = user_state
                user_updated = True
                print(f"Updated user state to: {user_state}")

            if profile_picture:
                request.user.profile_picture = profile_picture
                user_updated = True
                print(f"Updated user profile picture")

            if user_updated:
                request.user.save()
                print(f"User information saved successfully")

            # Only hospital managers can update hospital information
            if request.user.user_type == 'hospital_manager' and hospital:
                # Update hospital name
                name = request.POST.get('name')
                if name:
                    hospital.name = name
                    print(f"Updated hospital name to: {name}")
                
                # Update hospital subtitle
                sub_title = request.POST.get('sub_title')
                if sub_title:
                    hospital.sub_title = sub_title
                    print(f"Updated hospital subtitle to: {sub_title}")

                # Update hospital description
                description = request.POST.get('description')
                if description:
                    hospital.description = description
                    print(f"Updated hospital description")

                # Update hospital about section
                about = request.POST.get('about')
                if about:
                    hospital.about = about
                    print(f"Updated hospital about section")

                # Handle logo upload
                if 'logo' in request.FILES and request.FILES['logo']:
                    hospital.logo = request.FILES['logo']
                    print(f"Updated hospital logo")

                # Save the hospital object
                hospital.save()
                print(f"Hospital saved successfully")

                # Handle city selection
                city_id = request.POST.get('city_id')
                if city_id and city_id.isdigit():
                    try:
                        city = City.objects.get(id=city_id)
                        hospital.city = city
                        hospital.save()  # Save the hospital after updating the city
                        print(f"Updated hospital city to: {city.name}")
                    except City.DoesNotExist:
                        print(f"City with ID {city_id} not found")
                    except Exception as city_error:
                        print(f"Error updating city: {str(city_error)}")

                # Handle phone number updates
                try:
                    # Update existing phone numbers
                    for key, value in request.POST.items():
                        # Check for phone number updates
                        if key.startswith('phone_number_'):
                            phone_id = key.replace('phone_number_', '')
                            phone_type_key = f'phone_type_{phone_id}'
                            phone_type = request.POST.get(phone_type_key)

                            if phone_id.isdigit():
                                try:
                                    phone = PhoneNumber.objects.get(id=phone_id, hospital=hospital)
                                    phone.number = value
                                    if phone_type:
                                        phone.phone_type = phone_type
                                    phone.save()
                                    print(f"Updated phone number {phone_id} to {value} ({phone_type})")
                                except PhoneNumber.DoesNotExist:
                                    print(f"Phone number with ID {phone_id} not found")

                    # Handle phone number deletions
                    for key, value in request.POST.items():
                        if key.startswith('delete_phone_'):
                            phone_id = key.replace('delete_phone_', '')
                            if phone_id.isdigit():
                                try:
                                    phone = PhoneNumber.objects.get(id=phone_id, hospital=hospital)
                                    phone.delete()
                                    print(f"Deleted phone number {phone_id}")
                                except PhoneNumber.DoesNotExist:
                                    print(f"Phone number with ID {phone_id} not found for deletion")

                    # Add new phone numbers
                    for key, value in request.POST.items():
                        if key.startswith('new_phone_number_'):
                            counter = key.replace('new_phone_number_', '')
                            phone_type_key = f'new_phone_type_{counter}'
                            phone_type = request.POST.get(phone_type_key, 'mobile')

                            if value.strip():  # Only add if the number is not empty
                                PhoneNumber.objects.create(
                                    hospital=hospital,
                                    number=value,
                                    phone_type=phone_type,
                                    created_by=request.user
                                )
                                print(f"Added new phone number: {value} ({phone_type})")
                except Exception as phone_error:
                    print(f"Error handling phone numbers: {str(phone_error)}")
                    import traceback
                    traceback.print_exc()

            # Get the return section from the form data
            return_section = request.POST.get('return_section', 'doctor_profile_settings')
            
            if request.user.user_type == 'hospital_manager':
                messages.success(request, 'تم تحديث بيانات المستشفى بنجاح.')
            else:
                messages.success(request, 'تم تحديث بياناتك الشخصية بنجاح.')

            print(f"Redirecting to section: {return_section}")
            return redirect(f'/hospital/?section={return_section}')

        except Hospital.DoesNotExist:
            print("Hospital not found for current user")
            messages.error(request, 'لم يتم العثور على المستشفى المرتبط بالمستخدم الحالي.')
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'حدث خطأ أثناء تحديث البيانات: {e}.')
    else:
        print("Not a POST request")

    return redirect('/hospital/?section=doctor_profile_settings')

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
@csrf_exempt  # Note: We're keeping csrf_exempt for now but will handle CSRF manually
def update_doctor(request, doctor_id):
    print("="*50)
    print(f"Update doctor request method: {request.method}")
    print(f"CSRF Token in request: {request.META.get('HTTP_X_CSRFTOKEN', 'Not found')}")

    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')

    try:
        print("="*50)
        print(f"Updating doctor {doctor_id}")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        print(f"User type: {request.user.user_type}")

        # Get hospital based on user type
        hospital = None
        if request.user.user_type == 'hospital_manager':
            # If user is a hospital manager
            hospital = get_object_or_404(Hospital, user=request.user)
        elif hasattr(request.user, 'hospital_staff'):
            # If user is a hospital staff member
            hospital = request.user.hospital_staff.hospital

        if not hospital:
            print("Hospital not found for user")
            return JsonResponse({
                'status': 'error',
                'error': 'لم يتم العثور على المستشفى المرتبط بالمستخدم'
            }, status=403)

        # Get doctor
        doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
        print(f"Found doctor: {doctor.full_name}")

        try:
            # Update doctor information
            doctor.full_name = request.POST.get('full_name')
            print(f"Updated full_name: {doctor.full_name}")

            specialty_id = request.POST.get('specialty')
            if specialty_id:
                doctor.specialty_id = specialty_id
                print(f"Updated specialty_id: {doctor.specialty_id}")

            doctor.email = request.POST.get('email')
            print(f"Updated email: {doctor.email}")

            doctor.phone_number = request.POST.get('phone_number')
            print(f"Updated phone_number: {doctor.phone_number}")

            doctor.gender = request.POST.get('gender')
            print(f"Updated gender: {doctor.gender}")

            experience_years = request.POST.get('experience_years')
            if experience_years:
                doctor.experience_years = experience_years
                print(f"Updated experience_years: {doctor.experience_years}")

            doctor.status = request.POST.get('status') == '1'
            print(f"Updated status: {doctor.status}")

            doctor.about = request.POST.get('about', '')
            print(f"Updated about: {doctor.about}")

            # Handle photo upload
            if 'photo' in request.FILES:
                doctor.photo = request.FILES['photo']
                print(f"Updated photo: {doctor.photo}")

            doctor.save()
            print("Doctor saved successfully")

            # Update doctor price
            price = DoctorPricing.objects.filter(doctor=doctor, hospital=hospital).first()
            new_price = request.POST.get('pricing-0-amount')
            print(f"New price: {new_price}")

            if new_price:
                if price:
                    print(f"Updating existing price from {price.amount} to {new_price}")
                    # Create price history record
                    DoctorPricingHistory.objects.create(
                        doctor=doctor,
                        hospital=hospital,
                        amount=new_price,
                        previous_amount=price.amount,
                        created_by=request.user
                    )
                    # Update current price
                    price.amount = new_price
                    price.save()
                    print("Price updated successfully")
                else:
                    print(f"Creating new price: {new_price}")
                    # Create new price record
                    DoctorPricing.objects.create(
                        doctor=doctor,
                        hospital=hospital,
                        amount=new_price
                    )
                    print("New price created successfully")

            return JsonResponse({
                'status': 'success',
                'message': 'تم تحديث بيانات الطبيب بنجاح'
            })
        except Exception as inner_e:
            import traceback
            print(f"Inner error updating doctor: {str(inner_e)}")
            traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'error': f'حدث خطأ أثناء تحديث بيانات الطبيب: {str(inner_e)}'
            }, status=500)

    except Hospital.DoesNotExist:
        print("Hospital not found for user")
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على المستشفى المرتبط بالمستخدم'
        }, status=404)
    except Doctor.DoesNotExist:
        print("Doctor not found")
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على الطبيب'
        }, status=404)
    except Exception as e:
        import traceback
        print(f"Error updating doctor: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'error': f'حدث خطأ غير متوقع: {str(e)}'
        }, status=500)

@login_required(login_url='/user/login')
def delete_doctor(request, doctor_id):
    print("="*50)
    print(f"Delete doctor request method: {request.method}")
    print(f"Delete doctor URL path: {request.path}")
    print(f"CSRF Token in request: {request.META.get('HTTP_X_CSRFTOKEN', 'Not found')}")

    if request.method != 'POST':
        print(f"Invalid request method: {request.method}")
        return HttpResponseBadRequest('Invalid request method')

    try:
        print("="*50)
        print(f"Deleting doctor {doctor_id}")
        print(f"User type: {request.user.user_type}")

        # Get hospital based on user type
        hospital = None
        if request.user.user_type == 'hospital_manager':
            # If user is a hospital manager
            hospital = get_object_or_404(Hospital, user=request.user)
            print(f"Found hospital for manager: {hospital.name}")
        elif hasattr(request.user, 'hospital_staff'):
            # If user is a hospital staff member
            hospital = request.user.hospital_staff.hospital
            print(f"Found hospital for staff: {hospital.name}")
        else:
            print(f"User is neither hospital manager nor staff: {request.user.user_type}")

        if not hospital:
            print("Hospital not found for user")
            return JsonResponse({
                'status': 'error',
                'error': 'لم يتم العثور على المستشفى المرتبط بالمستخدم'
            }, status=403)

        try:
            # Get doctor
            doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
            print(f"Found doctor: {doctor.full_name}")

            # Remove the doctor from this hospital
            doctor.hospitals.remove(hospital)
            print(f"Removed doctor from hospital: {hospital.name}")

            # Delete the doctor's pricing for this hospital
            pricing_count = DoctorPricing.objects.filter(doctor=doctor, hospital=hospital).count()
            DoctorPricing.objects.filter(doctor=doctor, hospital=hospital).delete()
            print(f"Deleted {pricing_count} pricing records")

            # If the doctor is not associated with any other hospitals, delete the doctor
            hospitals_count = doctor.hospitals.count()
            print(f"Doctor is associated with {hospitals_count} hospitals")
            if hospitals_count == 0:
                doctor.delete()
                print(f"Deleted doctor completely as no more hospital associations")

            return JsonResponse({
                'status': 'success',
                'message': 'تم حذف الطبيب بنجاح'
            })
        except Exception as inner_e:
            import traceback
            print(f"Inner error deleting doctor: {str(inner_e)}")
            traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'error': f'حدث خطأ أثناء حذف الطبيب: {str(inner_e)}'
            }, status=500)

    except Hospital.DoesNotExist:
        print("Hospital not found for user")
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على المستشفى المرتبط بالمستخدم'
        }, status=404)
    except Doctor.DoesNotExist:
        print("Doctor not found")
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على الطبيب'
        }, status=404)
    except Exception as e:
        import traceback
        print(f"Error deleting doctor: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'error': f'حدث خطأ غير متوقع: {str(e)}'
        }, status=500)

@login_required(login_url='/user/login')
def get_doctor_history(request, doctor_id):
    try:
        print("="*50)
        print(f"Getting history for doctor {doctor_id}")
        print(f"User type: {request.user.user_type}")

        # Get hospital based on user type
        hospital = None
        if request.user.user_type == 'hospital_manager':
            # If user is a hospital manager
            hospital = get_object_or_404(Hospital, user=request.user)
        elif hasattr(request.user, 'hospital_staff'):
            # If user is a hospital staff member
            hospital = request.user.hospital_staff.hospital

        if not hospital:
            return JsonResponse({
                'status': 'error',
                'error': 'لم يتم العثور على المستشفى المرتبط بالمستخدم'
            }, status=403)

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

        history_data = [{
            'date': entry.change_date.strftime('%Y-%m-%d %H:%M'),
            'amount': str(entry.amount),
            'previous_amount': str(entry.previous_amount) if entry.previous_amount else None,
            'created_by': entry.created_by.get_full_name() if entry.created_by else None
        } for entry in history]

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
        print("Hospital not found for user")
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على المستشفى المرتبط بالمستخدم'
        }, status=404)
    except Doctor.DoesNotExist:
        print("Doctor not found")
        return JsonResponse({
            'status': 'error',
            'error': 'لم يتم العثور على الطبيب'
        }, status=404)
    except Exception as e:
        import traceback
        print(f"Error getting doctor history: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'error': f'حدث خطأ غير متوقع: {str(e)}'
        }, status=500)

@login_required(login_url='/user/login')
def search_doctors(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        search_query = request.GET.get('query', '')
        current_hospital = get_object_or_404(Hospital, user=request.user)

        # البحث عن الأطباء باستخدام الاسم أو التخصص
        doctors = Doctor.objects.filter(
            Q(full_name__icontains=search_query) |
            Q(specialty__name__icontains=search_query)
        ).exclude(hospitals=current_hospital).distinct()

        doctors_data = []
        for doctor in doctors:
            current_hospitals = doctor.hospitals.all()
            doctors_data.append({
                'id': doctor.id,
                'full_name': doctor.full_name,
                'specialty': doctor.specialty.name if doctor.specialty else '',
                'current_hospitals': [h.name for h in current_hospitals],
                'photo_url': doctor.photo.url if doctor.photo else None
            })

        return JsonResponse({'doctors': doctors_data})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='/user/login')
def add_existing_doctor(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        amount = request.POST.get('amount')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            hospital = get_object_or_404(Hospital, user=request.user)

            # إضافة الطبيب إلى المستشفى
            doctor.hospitals.add(hospital)

            # إنشاء تسعيرة للطبيب في المستشفى
            DoctorPricing.objects.create(
                doctor=doctor,
                hospital=hospital,
                amount=amount
            )

            return JsonResponse({
                'status': 'success',
                'message': 'تم إضافة الطبيب بنجاح'
            })

        except Doctor.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'لم يتم العثور على الطبيب'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'طريقة الطلب غير صحيحة'
    }, status=400)

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
        print(f"User type: {request.user.user_type}")

        # Get hospital based on user type
        hospital = None
        if request.user.user_type == 'hospital_manager':
            # If user is a hospital manager
            hospital = get_object_or_404(Hospital, user=request.user)
        elif hasattr(request.user, 'hospital_staff'):
            # If user is a hospital staff member
            hospital = request.user.hospital_staff.hospital

        if not hospital:
            messages.error(request, 'لم يتم العثور على المستشفى المرتبط بالمستخدم')
            return redirect('hospitals:index')

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
