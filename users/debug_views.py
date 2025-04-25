from django.shortcuts import render
from django.contrib.auth import authenticate
from .models import CustomUser
from hospital_staff.models import HospitalStaff

def debug_login(request):
    """وظيفة تصحيح لتسجيل الدخول"""
    context = {}
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # التحقق من وجود المستخدم
        try:
            user_exists = CustomUser.objects.filter(email=email).exists()
            if user_exists:
                user_obj = CustomUser.objects.get(email=email)
                context['user_exists'] = True
                context['user_email'] = user_obj.email
                context['user_type'] = user_obj.user_type
                context['user_id'] = user_obj.id
                
                # التحقق من كلمة المرور
                auth_user = authenticate(username=email, password=password)
                context['password_correct'] = auth_user is not None
                
                # التحقق من وجود سجل موظف
                if user_obj.user_type == 'hospital_staff':
                    try:
                        staff = HospitalStaff.objects.get(user=user_obj)
                        context['staff_exists'] = True
                        context['staff_id'] = staff.id
                        context['staff_hospital'] = staff.hospital.name
                        context['staff_role'] = staff.role.name if staff.role else 'لا يوجد'
                    except HospitalStaff.DoesNotExist:
                        context['staff_exists'] = False
            else:
                context['user_exists'] = False
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'frontend/auth/debug_login.html', context)
