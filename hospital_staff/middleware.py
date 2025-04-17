from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import HospitalStaff

class StaffPermissionMiddleware:
    """
    وسيط للتحقق من صلاحيات موظفي المستشفى
    
    يتحقق من أن المستخدم لديه الصلاحية المطلوبة للوصول إلى الصفحة
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # تنفيذ الكود قبل معالجة الطلب
        
        # إذا كان المستخدم مسجل الدخول وهو موظف مستشفى
        if request.user.is_authenticated and request.user.user_type == 'hospital_staff':
            # التحقق من وجود سجل للموظف
            try:
                staff = HospitalStaff.objects.get(user=request.user)
                
                # التحقق من حالة الموظف
                if staff.status != 'active':
                    # إذا كان الموظف غير نشط، قم بتسجيل خروجه وإعادة توجيهه
                    messages.error(request, _("حسابك غير نشط. يرجى التواصل مع مدير المستشفى"))
                    return redirect('users:logout')
                
                # إضافة كائن الموظف إلى الطلب لاستخدامه لاحقًا
                request.staff = staff
                
            except HospitalStaff.DoesNotExist:
                # إذا لم يكن هناك سجل للموظف، قم بتسجيل خروجه وإعادة توجيهه
                messages.error(request, _("لم يتم العثور على سجل موظف لحسابك. يرجى التواصل مع مدير المستشفى"))
                return redirect('users:logout')
        
        # معالجة الطلب
        response = self.get_response(request)
        
        # تنفيذ الكود بعد معالجة الطلب
        
        return response
