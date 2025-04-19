from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect ,reverse
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pydantic import ValidationError, validate_email
from django.utils.translation import gettext_lazy as _

from hospitals.models import HospitalAccountRequest
from .models import CustomUser
from patients.models import Patients
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout




def patient_signup(request):
    """عرض صفحة تسجيل المريض ومعالجة البيانات"""
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # تحقق من تطابق كلمتي المرور
        if password != confirm_password:
            return render(request, 'frontend/auth/patient-signup.html', {
                'error': 'كلمتا المرور غير متطابقتين.'
            })

        # التحقق من أن اسم المستخدم والبريد غير مستخدمين مسبقًا
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'frontend/auth/patient-signup.html', {
                'error': 'اسم المستخدم مستخدم بالفعل.'
            })

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'frontend/auth/patient-signup.html', {
                'error': 'البريد الإلكتروني مستخدم بالفعل.'
            })

        # تخزين البيانات في الجلسة
        request.session['username'] = username
        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['email'] = email
        request.session['mobile_number'] = mobile_number
        request.session['password'] = password

        return redirect('users:register_step1')

    return render(request, 'frontend/auth/patient-signup.html')


def register_step1(request):
    """الخطوة الثانية من التسجيل: رفع الصورة وإدخال بيانات العنوان."""
    if request.method == "POST":
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            path = default_storage.save(f'uploads/profile_pictures/{profile_image.name}', ContentFile(profile_image.read()))
            request.session['profile_image'] = path

        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')

        # حفظ البيانات في الجلسة
        request.session['birth_date'] = birth_date
        request.session['gender'] = gender
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state

        return redirect('users:register_step2') 

    return render(request, 'frontend/auth/patient-register-step1.html')


def register_step2(request):
    """الخطوة الثالثة من التسجيل: إدخال بيانات المريض وحفظها مباشرة."""
    if request.method == "POST":
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        age = request.POST.get('age')
        blood_group = request.POST.get('blood_group')
        notes = request.POST.get('notes')

        # استرجاع بيانات الجلسة
        username = request.session.get('username')
        first_name = request.session.get('first_name')
        last_name = request.session.get('last_name')
        email = request.session.get('email')
        mobile_number = request.session.get('mobile_number')
        password = request.session.get('password')
        profile_picture = request.session.get('profile_image')
        address = request.session.get('address')
        city = request.session.get('city')
        state = request.session.get('state')
        birth_date = request.session.get('birth_date')
        gender = request.session.get('gender')

        # التحقق من أن جميع البيانات موجودة
        if not all([username, first_name, last_name, email, mobile_number, password, profile_picture, address, city, state]):
            return render(request, 'frontend/auth/patient-register-step1.html', {
                'error': 'حدث خطأ في البيانات. تأكد من إدخال جميع البيانات.'
            })

        # إنشاء المستخدم
        user = CustomUser.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile_number,
            password=password,
            profile_picture=profile_picture,
            address=address,
            city=city,
            state=state,
            user_type='patient',
        )

        # إنشاء سجل مريض في جدول Patients
        Patients.objects.create(
            user=user,
            birth_date=birth_date,
            gender=gender,
        )

        # مسح الجلسة بعد التسجيل
        request.session.flush()

        # تسجيل الدخول مباشرة بعد التسجيل
        login(request, user)

        # التوجه إلى لوحة تحكم المريض
        return redirect('patients:patient_dashboard')

    return render(request, 'frontend/auth/patient-register-step1.html')


def patient_dashboard(request):
    """عرض صفحة لوحة تحكم المريض بعد التسجيل."""
    return render(request, 'frontend/dashboard/patient/index.html')


def admin_dashboard(request):
    return render(request, 'frontend/dashboard/admin/index.html')

# @login_required(login_url='/user/login')

# def doctor_dashboard(request):
#     return render(request, 'frontend/dashboard/doctor/index.html')

from django.contrib.auth.hashers import make_password, check_password
def login_view(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next')

        print(f"\n\nمحاولة تسجيل دخول: {email}, {password}\n\n")

        try:
            user_exists = CustomUser.objects.filter(email=email).exists()
            if user_exists:
                user_obj = CustomUser.objects.get(email=email)
                print(f"\n\nالمستخدم موجود: {user_obj.email}, نوع المستخدم: {user_obj.user_type}\n\n")
            else:
                print(f"\n\nالمستخدم غير موجود: {email}\n\n")
        except Exception as e:
            print(f"\n\nخطأ في التحقق من وجود المستخدم: {str(e)}\n\n")

        user = authenticate(request, username=email, password=password)

        print(f"\n\nنتيجة المصادقة: {user}\n\n")

        if user is not None:
            login(request, user)
            print(f"\n\nنوع المستخدم: {user.user_type}\n\n")

            # أول تسجيل دخول لموظف المستشفى
            if user.user_type == 'hospital_staff':
                try:
                    from hospital_staff.models import HospitalStaff
                    staff = HospitalStaff.objects.get(user=user)
                    if staff.is_first_login:
                        return redirect('hospital_staff:first_login_change_password')
                except Exception as e:
                    print(f"\n\nخطأ في التحقق من أول تسجيل دخول: {str(e)}\n\n")

            # توجيه بناء على `next`
            if next_url:
                return redirect(next_url)

            # توجيه حسب نوع المستخدم
            if user.user_type == 'admin':
                return redirect(reverse('users:admin_dashboard'))
            elif user.user_type == 'hospital_manager':
                return redirect(reverse('hospitals:index'))
            elif user.user_type == 'hospital_staff':
                try:
                    from hospital_staff.models import HospitalStaff
                    staff = HospitalStaff.objects.get(user=user)
                    print(f"\n\nتم توجيه الموظف إلى لوحة تحكم المستشفى: {staff.hospital.name}\n\n")
                    return redirect(reverse('hospitals:index'))
                except Exception as e:
                    print(f"\n\nخطأ في توجيه الموظف: {str(e)}\n\n")
                    messages.error(request, _("حدث خطأ في توجيهك إلى لوحة التحكم. يرجى التواصل مع مدير النظام."))
                    return redirect(reverse('users:logout'))
            elif user.user_type == 'patient':
                return redirect(reverse('patients:patient_dashboard'))
            else:
                messages.error(request, "User type is not recognized.")
                return redirect(reverse('users:login'))
        else:
            try:
                user_exists = CustomUser.objects.filter(email=email).exists()
                if user_exists:
                    messages.error(request, "كلمة المرور غير صحيحة. الرجاء المحاولة مرة أخرى.")
                else:
                    messages.error(request, "البريد الإلكتروني غير مسجل في النظام.")
            except Exception as e:
                print(f"\n\nخطأ في التحقق من رسالة الخطأ: {str(e)}\n\n")
                messages.error(request, "حدث خطأ أثناء تسجيل الدخول. الرجاء المحاولة مرة أخرى.")

            return redirect(reverse('users:login'))

    return render(request, 'frontend/auth/login.html')

def user_logout(request):
    logout(request)
    return redirect('/')


def hospital_account_request(request):
    if request.method == 'POST':
        try:
            # استخلاص البيانات من الطلب
            hospital_name = request.POST.get('hospital_name')
            manager_full_name = request.POST.get('manager_full_name')
            manager_email = request.POST.get('manager_email')
            manager_phone = request.POST.get('manager_phone')
            logo = request.FILES.get('logo')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            hospital_location = request.POST.get('hospital_location')
            notes = request.POST.get('notes', '')
            commercial_record = request.FILES.get('commercial_record')
            medical_license = request.FILES.get('medical_license')

            # 1. التحقق من الحقول المطلوبة
            if not all([hospital_name, manager_full_name, manager_email, manager_phone,logo, password, confirm_password, hospital_location]):
                messages.error(request, 'الرجاء ملء جميع الحقول المطلوبة.')
                return render(request, 'frontend/auth/hospital-manager-register.html', request.POST)

            # 2. التحقق من صحة البريد الإلكتروني
            try:
              validate_email(manager_email)
            except ValidationError:
                messages.error(request, 'البريد الإلكتروني غير صالح.')
                return render(request, 'frontend/auth/hospital-manager-register.html', request.POST)

            # 3. التحقق من تطابق كلمتي المرور
            if password != confirm_password:
                messages.error(request, 'كلمتا المرور غير متطابقتين.')
                return render(request, 'frontend/auth/hospital-manager-register.html', request.POST)

            # # 4. التحقق من صحة رقم الهاتف (يمكنك إضافة شروط أكثر تعقيدًا إذا لزم الأمر)
            # if not manager_phone.isdigit() or len(manager_phone) < 9:
            #      messages.error(request, 'رقم الهاتف غير صالح.')
            #      return render(request, 'frontend/auth/hospital-manager-register.html', request.POST)

            #  # 5. التحقق من حجم الملفات (يمكنك تعديل الحجم الأقصى حسب الحاجة)
            # max_file_size = settings.MAX_UPLOAD_SIZE
            # if commercial_record and commercial_record.size > max_file_size:
            #       messages.error(request, f'حجم السجل التجاري كبير جدًا. الحد الأقصى هو {max_file_size / (1024 * 1024) } ميجابايت')
            #       return render(request, 'frontend/auth/hospital-manager-register.html', request.POST)
            # if medical_license and medical_license.size > max_file_size:
            #      messages.error(request, f'حجم الترخيص الطبي كبير جدًا. الحد الأقصى هو {max_file_size / (1024 * 1024) } ميجابايت')
            #      return render(request, 'frontend/auth/hospital-manager-register.html', request.POST)

            # إنشاء طلب جديد
            hospital_request = HospitalAccountRequest(
                hospital_name=hospital_name,
                manager_full_name=manager_full_name,
                manager_email=manager_email,
                manager_phone=manager_phone,
                logo=logo,
                manager_password=password,
                hospital_location=hospital_location,
                notes=notes,
                created_by=request.user if request.user.is_authenticated else None
            )

            # معالجة الملفات المرفقة
            if commercial_record:
                hospital_request.commercial_record = commercial_record
            if medical_license:
                hospital_request.medical_license = medical_license

            hospital_request.save()

            messages.success(request, 'تم استلام طلبك بنجاح. سنقوم بمراجعته والرد عليك قريباً.')
            return redirect('hospitals:hospital_request_success')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء معالجة طلبك: {e}. يرجى المحاولة مرة أخرى.')
            return render(request, 'frontend/auth/hospital-manager-register.html', request.POST)

    return render(request, 'frontend/auth/hospital-manager-register.html')




from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect
import logging


#تغيير كلمة السر للمريض و مدير المستشفى
logger = logging.getLogger(__name__)

def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'كلمة المرور القديمة غير صحيحة.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if new_password != confirm_password:
            messages.error(request, 'كلمة المرور الجديدة وتأكيد كلمة المرور لا يتطابقان.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        logger.info(f'Password successfully changed for user {request.user.username}')
        messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect(request.META.get('HTTP_REFERER', '/'))
