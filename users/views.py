from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import login
from .models import CustomUser
from . import views


class LoginView(auth_views.LoginView):
    template_name = 'frontend\auth\login.html'

    def get_success_url(self):
        return reverse_lazy('frontend\dashboard\patient\index.html')


class LogoutView(auth_views.LogoutView):
    next_page = 'login'


class IndexView(TemplateView):
    template_name = 'frontend\home\index.html'


def patient_signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        password = make_password(request.POST.get('password'))

        # تخزين بيانات الجلسة
        request.session['name'] = name
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
        is_pregnant = request.POST.get('is_pregnant') == '1'
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
        return redirect('register_step3')
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
        return redirect('register_step4')
    return render(request, 'frontend/auth/patient-register-step3.html')


def register_step4(request):
    if request.method == "POST":
        city = request.POST.get('city')
        state = request.POST.get('state')

        request.session['city'] = city
        request.session['state'] = state
        return redirect('register_step5')
    return render(request, 'frontend/auth/patient-register-step4.html')


def register_step5(request):
    if request.method == "POST":
        # حفظ بيانات المستخدم النهائية
        user = CustomUser(
            username=request.session['name'],
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
        )
        user.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'frontend/auth/patient-register-step4.html')


def dashboard(request):
    return render(request, 'frontend/dashboard/patient/index.html', {'user': request.user})
