from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden

from hospitals.models import Hospital
from .models import HospitalStaff, StaffPermission, StaffAdditionalPermission

def has_permission(permission_codename):
    """
    مصمم للتحقق من صلاحيات موظفي المستشفى
    
    يستخدم كـ decorator للتحقق من أن المستخدم لديه الصلاحية المطلوبة
    إما من خلال دوره الوظيفي أو من خلال الصلاحيات الإضافية
    
    مثال الاستخدام:
    
    @has_permission('manage_doctors')
    def some_view(request):
        # ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # التحقق من تسجيل الدخول
            if not request.user.is_authenticated:
                return redirect('users:login')
            
            # إذا كان المستخدم مدير مستشفى، فلديه جميع الصلاحيات
            if request.user.user_type == 'hospital_manager':
                return view_func(request, *args, **kwargs)
            
            # إذا كان المستخدم ليس موظف مستشفى، فليس لديه صلاحية
            if request.user.user_type != 'hospital_staff':
                messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
                return redirect('hospitals:index')
            
            # التحقق من وجود سجل للموظف
            try:
                staff = HospitalStaff.objects.get(user=request.user)
            except HospitalStaff.DoesNotExist:
                messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
                return redirect('hospitals:index')
            
            # التحقق من حالة الموظف
            if staff.status != 'active':
                messages.error(request, _("حسابك غير نشط. يرجى التواصل مع مدير المستشفى"))
                return redirect('hospitals:index')
            
            # التحقق من الصلاحية من خلال الدور الوظيفي
            if staff.role and staff.role.permissions.filter(codename=permission_codename).exists():
                return view_func(request, *args, **kwargs)
            
            # التحقق من الصلاحيات الإضافية
            try:
                permission = StaffPermission.objects.get(codename=permission_codename)
                additional_permission = StaffAdditionalPermission.objects.get(
                    staff=staff,
                    permission=permission
                )
                if additional_permission.granted:
                    return view_func(request, *args, **kwargs)
            except (StaffPermission.DoesNotExist, StaffAdditionalPermission.DoesNotExist):
                pass
            
            # إذا وصلنا إلى هنا، فالمستخدم ليس لديه الصلاحية المطلوبة
            messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
            return redirect('hospitals:index')
        
        return _wrapped_view
    
    return decorator

def check_permission(user, permission_codename):
    """
    التحقق من صلاحية المستخدم
    
    تستخدم للتحقق من صلاحية المستخدم في القوالب أو في الكود
    
    مثال الاستخدام:
    
    if check_permission(request.user, 'manage_doctors'):
        # ...
    """
    # إذا كان المستخدم مدير مستشفى، فلديه جميع الصلاحيات
    if user.user_type == 'hospital_manager':
        return True
    
    # إذا كان المستخدم ليس موظف مستشفى، فليس لديه صلاحية
    if user.user_type != 'hospital_staff':
        return False
    
    # التحقق من وجود سجل للموظف
    try:
        staff = HospitalStaff.objects.get(user=user)
    except HospitalStaff.DoesNotExist:
        return False
    
    # التحقق من حالة الموظف
    if staff.status != 'active':
        return False
    
    # التحقق من الصلاحية من خلال الدور الوظيفي
    if staff.role and staff.role.permissions.filter(codename=permission_codename).exists():
        return True
    
    # التحقق من الصلاحيات الإضافية
    try:
        permission = StaffPermission.objects.get(codename=permission_codename)
        additional_permission = StaffAdditionalPermission.objects.get(
            staff=staff,
            permission=permission
        )
        return additional_permission.granted
    except (StaffPermission.DoesNotExist, StaffAdditionalPermission.DoesNotExist):
        return False
