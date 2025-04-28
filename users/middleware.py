from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _
from hospital_staff.models import HospitalStaff

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # طباعة المسار الذي يتم الوصول إليه
        print(f"\n\n*** المسار المطلوب: {request.path} ***\n\n")

        # استثناء صفحة تسجيل الدخول وصفحة نجاح طلب فتح حساب المستشفى
        if request.path == '/users/login/' or request.path == '/hospital/account/request/success/':
            print(f"\n\n*** السماح بالوصول إلى المسار: {request.path} ***\n\n")
            return self.get_response(request)

        if request.user.is_authenticated:
            user_role = request.user.user_type

            # التحقق من حالة موظف المستشفى (نشط/غير نشط/موقوف)
            if user_role == 'hospital_staff':
                try:
                    staff = HospitalStaff.objects.get(user=request.user)
                    if staff.status == 'inactive':
                        messages.error(request, _('حسابك غير نشط. يرجى التواصل مع مدير المستشفى.'))
                        logout(request)
                        return redirect('users:login')
                    elif staff.status == 'suspended':
                        messages.error(request, _('حسابك موقوف. يرجى التواصل مع مدير المستشفى.'))
                        logout(request)
                        return redirect('users:login')
                except HospitalStaff.DoesNotExist:
                    # إذا لم يكن هناك سجل للموظف، قم بتوجيهه إلى صفحة تسجيل الدخول
                    messages.error(request, _('لم يتم العثور على سجل موظف لحسابك. يرجى التواصل مع مدير المستشفى.'))
                    logout(request)
                    return redirect('users:login')

            # Define restricted routes and their allowed roles
            restricted_routes = {
                '/hospital/': ['hospital_manager', 'hospital_staff'],  # السماح لمدير المستشفى وموظفي المستشفى
                '/patients/': 'patient',
            }

            # Check if the requested path is a restricted route
            for restricted_path, allowed_role in restricted_routes.items():
                if request.path.startswith(restricted_path):
                    # If the user's role doesn't match, redirect to login
                    if isinstance(allowed_role, list):
                        # إذا كانت الأدوار المسموح بها قائمة
                        if user_role not in allowed_role:
                            print(f"\n\n*** المستخدم ليس لديه دور مسموح به: {user_role} ***\n\n")
                            return redirect('/')
                    else:
                        # إذا كان الدور المسموح به قيمة واحدة
                        if user_role != allowed_role:
                            print(f"\n\n*** المستخدم ليس لديه دور مسموح به: {user_role} ***\n\n")
                            return redirect('/')

        elif request.path.startswith('/hospital/') or request.path.startswith('/patients/'):
            # التحقق مرة أخرى من صفحة نجاح الطلب
            if request.path == '/hospital/account/request/success/':
                print("\n\n*** السماح بالوصول إلى صفحة نجاح طلب فتح حساب المستشفى ***\n\n")
                return self.get_response(request)

            print("\n\n*** محاولة الوصول إلى مسار محمي: {} ***\n\n".format(request.path))
            return redirect('/users/login/')

        return self.get_response(request)
