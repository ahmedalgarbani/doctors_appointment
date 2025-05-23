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
    # Clear the hospital_user_message from session after displaying it
    hospital_user_message = None
    if 'hospital_user_message' in request.session:
        hospital_user_message = request.session.pop('hospital_user_message')

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
    # التحقق من وجود البيانات الأساسية في الجلسة
    username = request.session.get('username')
    if not username:
        messages.error(request, 'يرجى إكمال بيانات الحساب الأساسية أولاً')
        return redirect('users:patient_signup')

    if request.method == "POST":
        # معالجة صورة الملف الشخصي
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            try:
                path = default_storage.save(f'uploads/profile_pictures/{profile_image.name}', ContentFile(profile_image.read()))
                request.session['profile_image'] = path
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء رفع الصورة: {str(e)}')
                return render(request, 'frontend/auth/patient-register-step1.html')

        # استخراج البيانات من النموذج
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')

        # التحقق من البيانات المطلوبة
        if not address:
            messages.error(request, 'يرجى إدخال العنوان')
            return render(request, 'frontend/auth/patient-register-step1.html')

        if not city:
            messages.error(request, 'يرجى إدخال المدينة')
            return render(request, 'frontend/auth/patient-register-step1.html')

        # حفظ البيانات في الجلسة
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state

        # تهيئة بيانات الخطوة الثانية
        if 'step2_data' not in request.session:
            request.session['step2_data'] = {}

        request.session.modified = True
        return redirect('users:register_step2')

    return render(request, 'frontend/auth/patient-register-step1.html')


def register_step2(request):
    """الخطوة الثالثة من التسجيل: إدخال بيانات المريض وحفظها مباشرة."""
    # تحضير البيانات للعرض في القالب
    if 'step2_data' not in request.session:
        request.session['step2_data'] = {}

    # استرجاع بيانات الجلسة الأساسية للتحقق
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

    # التحقق من أن البيانات الأساسية موجودة
    if not all([username, first_name, last_name, email, mobile_number, password]):
        messages.error(request, 'بيانات الحساب غير مكتملة. يرجى العودة وإكمال البيانات الأساسية.')
        return redirect('users:patient_signup')

    if request.method == "POST":
        # استخراج البيانات من النموذج
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        notes = request.POST.get('notes', '')

        # حفظ البيانات في الجلسة للعرض في حالة الخطأ
        request.session['step2_data'] = {
            'birth_date': birth_date,
            'gender': gender,
            'notes': notes
        }

        # التحقق من البيانات المطلوبة
        if not birth_date:
            messages.error(request, 'يرجى إدخال تاريخ الميلاد')
            return render(request, 'frontend/auth/patient-register-step2.html')

        if not gender:
            messages.error(request, 'يرجى اختيار الجنس')
            return render(request, 'frontend/auth/patient-register-step2.html')

        try:
            # إنشاء المستخدم
            user = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile_number=mobile_number,
                password=password,
                address=address,
                city=city,
                state=state,
                user_type='patient',
            )

            # إضافة صورة الملف الشخصي إذا كانت موجودة
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()

            # إنشاء سجل مريض في جدول Patients
            patient = Patients.objects.create(
                user=user,
                birth_date=birth_date,
                gender=gender,
                notes=notes
            )

            # مسح الجلسة بعد التسجيل
            request.session.flush()

            # تسجيل الدخول مباشرة بعد التسجيل
            login(request, user)

            # إضافة رسالة نجاح
            messages.success(request, 'تم إنشاء حسابك بنجاح!')

            # التوجه إلى لوحة تحكم المريض
            return redirect('patients:patient_dashboard')

        except Exception as e:
            # في حالة حدوث خطأ، عرض رسالة الخطأ
            messages.error(request, f'حدث خطأ أثناء إنشاء الحساب: {str(e)}')
            return render(request, 'frontend/auth/patient-register-step2.html')

    # في حالة GET، عرض الصفحة مع البيانات المخزنة في الجلسة

    request.session.modified = True
    return render(request, 'frontend/auth/patient-register-step2.html')


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

    # Check if there's a message parameter in the URL
    if request.GET.get('message') == 'login_required' and 'login_required_message' not in request.session:
        request.session['login_required_message'] = 'يجب تسجيل الدخول أولاً لحجز موعد مع الطبيب'

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

            # توجيه بناء على `next` أو redirect_after_login من الجلسة
            if 'redirect_after_login' in request.session:
                redirect_url = request.session.pop('redirect_after_login')
                # Clear the login message from session
                if 'login_required_message' in request.session:
                    del request.session['login_required_message']
                return redirect(redirect_url)
            elif next_url:
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
            if not all([hospital_name, manager_full_name, manager_email, manager_phone, password, confirm_password, hospital_location]):
                messages.error(request, 'الرجاء ملء جميع الحقول المطلوبة.')
                return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

            # التحقق من الملفات المطلوبة
            if not logo:
                messages.error(request, 'الرجاء رفع شعار المستشفى.')
                return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

            if not commercial_record:
                messages.error(request, 'الرجاء رفع السجل التجاري.')
                return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

            if not medical_license:
                messages.error(request, 'الرجاء رفع الترخيص الطبي.')
                return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

            # 2. التحقق من صحة البريد الإلكتروني
            try:
              validate_email(manager_email)
            except ValidationError:
                messages.error(request, 'البريد الإلكتروني غير صالح.')
                return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

            # 3. التحقق من تطابق كلمتي المرور
            if password != confirm_password:
                messages.error(request, 'كلمتا المرور غير متطابقتين.')
                return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

            # 4. التحقق من صحة رقم الهاتف
            if not manager_phone.isdigit() or len(manager_phone) < 9:
                 messages.error(request, 'رقم الهاتف غير صالح. يجب أن يتكون من أرقام فقط ولا يقل عن 9 أرقام.')
                 return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

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
                commercial_record=commercial_record,
                medical_license=medical_license,
                created_by=request.user if request.user.is_authenticated else None
            )

            hospital_request.save()

            messages.success(request, 'تم استلام طلبك بنجاح. سنقوم بمراجعته والرد عليك قريباً.')
            print("\n\n*** تم حفظ طلب فتح حساب المستشفى بنجاح. جاري التوجيه إلى صفحة النجاح ***\n\n")
            # استخدام اسم المسار للتوجيه بدلاً من المسار المطلق
            from django.urls import reverse
            success_url = reverse('users:hospital_request_success')
            print(f"\n\n*** جاري التوجيه إلى: {success_url} ***\n\n")
            return redirect(success_url)

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء معالجة طلبك: {e}. يرجى المحاولة مرة أخرى.')
            return render(request, 'frontend/auth/hospital-manager-register.html', {'form_data': request.POST})

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
