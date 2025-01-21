from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import login
from pydantic import ValidationError, validate_email

from hospitals.models import HospitalAccountRequest
from .models import CustomUser
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import CustomUser

def login_view(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user) 
            
            next_url = request.GET.get('next', None)
            if next_url:
                return redirect(next_url)
            
            if user.user_type == 'admin':
                return redirect(reverse('users:admin_dashboard'))
            elif user.user_type == 'hospital_manager':
                return redirect(reverse('hospitals:index'))
            elif user.user_type == 'patient':
                return redirect(reverse('patients:patient_dashboard'))
            else:
                messages.error(request, "User type is not recognized.")
                return redirect(reverse('users:login'))
        else:
            messages.error(request, "Invalid email or password.")
            return redirect(reverse('users:login'))

    return render(request, 'frontend/auth/login.html')



from django.shortcuts import redirect
from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    return redirect('/')


def patient_signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        password = make_password(request.POST.get('password'))

        # تخزين بيانات الجلسة
        request.session['name'] = name
        request.session['email'] = email
        request.session['mobile_number'] = mobile_number
        request.session['password'] = password

        return redirect('users:register_step1')
    return render(request, 'frontend/auth/patient-signup.html')


def register_step1(request):
    if request.method == "POST":
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            path = default_storage.save(f'uploads/profile_pictures/{profile_picture.name}', ContentFile(profile_picture.read()))
            request.session['profile_picture'] = path
        return redirect('users:register_step2')
    return render(request, 'frontend/auth/patient-register-step1.html')


def register_step2(request):
    if request.method == "POST":
        gender = request.POST.get('gender')
        is_pregnant = request.POST.get('is_pregnant') == 'on'
        pregnancy_term = request.POST.get('pregnancy_term')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        age = request.POST.get('age')
        blood_group = request.POST.get('blood_group')

        request.session['step2_data'] = {
            'gender': gender,
            'is_pregnant': is_pregnant,
            'pregnancy_term': pregnancy_term,
            'weight': weight,
            'height': height,
            'age': age,
            'blood_group': blood_group,
        }
        return redirect('users:register_step3')
    return render(request, 'frontend/auth/patient-register-step2.html')


def register_step3(request):
    if request.method == "POST":
        family_data = {
            'self': request.POST.get('self') == '1',
            'spouse': request.POST.get('spouse') == '1',
            'child_count': int(request.POST.get('child', 0)),
            'mother': request.POST.get('mother') == '1',
            'father': request.POST.get('father') == '1',
        }
        request.session['family_data'] = family_data
        return redirect('users:register_step4')
    return render(request, 'frontend/auth/patient-register-step3.html')


def register_step4(request):
    if request.method == "POST":
        city = request.POST.get('city')
        state = request.POST.get('state')

        request.session['city'] = city
        request.session['state'] = state
        return redirect('users:register_step5')
    return render(request, 'frontend/auth/patient-register-step4.html')


def register_step5(request):
    if request.method == "POST":
        # حفظ بيانات المستخدم النهائية
        user = CustomUser(
            username=request.session['name'],
            email=request.session['email'],
            mobile_number=request.session['mobile_number'],
            password=request.session['password'],
            profile_picture=request.session.get('profile_picture', None),
            gender=request.session['step2_data']['gender'],
            is_pregnant=request.session['step2_data']['is_pregnant'],
            pregnancy_term=request.session['step2_data']['pregnancy_term'],
            weight=request.session['step2_data']['weight'],
            height=request.session['step2_data']['height'],
            age=request.session['step2_data']['age'],
            blood_group=request.session['step2_data']['blood_group'],
            family_data=request.session['family_data'],
            city=request.session['city'],
            state=request.session['state'],
            user_type='patient'  # تحديد نوع المستخدم كمريض
        )
        user.save()
        login(request, user)
        return redirect('users:patient_dashboard')
    return render(request, 'frontend/auth/patient-register-step5.html')



def patient_dashboard(request):
    return render(request, 'frontend/dashboard/patient/index.html')


def admin_dashboard(request):
    return render(request, 'frontend/dashboard/admin/index.html')

# @login_required(login_url='/user/login')

# def doctor_dashboard(request):
#     return render(request, 'frontend/dashboard/doctor/index.html')


def hospital_account_request(request):
    if request.method == 'POST':
        try:
            # استخلاص البيانات من الطلب
            hospital_name = request.POST.get('hospital_name')
            manager_full_name = request.POST.get('manager_full_name')
            manager_email = request.POST.get('manager_email')
            manager_phone = request.POST.get('manager_phone')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            hospital_location = request.POST.get('hospital_location')
            notes = request.POST.get('notes', '')
            commercial_record = request.FILES.get('commercial_record')
            medical_license = request.FILES.get('medical_license')
            
            # 1. التحقق من الحقول المطلوبة
            if not all([hospital_name, manager_full_name, manager_email, manager_phone, password, confirm_password, hospital_location]):
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
