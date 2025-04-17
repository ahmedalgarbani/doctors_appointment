from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import HospitalStaff, StaffRole, StaffPermission, StaffAdditionalPermission
from hospitals.models import Hospital
from .forms import StaffForm, StaffEditForm, RoleForm

User = get_user_model()

# ===== إدارة الموظفين =====

@login_required
def staff_list(request):
    """عرض قائمة موظفي المستشفى"""
    # التحقق من أن المستخدم هو مدير مستشفى
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    # الحصول على المستشفى الخاص بالمستخدم
    hospital = get_object_or_404(Hospital, user=request.user)

    # الحصول على قائمة الموظفين
    staff_list = HospitalStaff.objects.filter(hospital=hospital).select_related('user', 'role')

    context = {
        'staff_list': staff_list,
        'hospital': hospital,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/staff-list.html', context)

@login_required
def add_staff(request):
    """إضافة موظف جديد"""
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    hospital = get_object_or_404(Hospital, user=request.user)
    roles = StaffRole.objects.filter(hospital=hospital)

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
                    email = form.cleaned_data['email']
                    if User.objects.filter(email=email).exists():
                        messages.error(request, _("البريد الإلكتروني مستخدم بالفعل"))
                        return redirect('hospital_staff:add_staff')

                    # إنشاء حساب المستخدم
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        mobile_number=form.cleaned_data['mobile_number'],
                        user_type='hospital_staff',
                    )

                    if form.cleaned_data['profile_picture']:
                        user.profile_picture = form.cleaned_data['profile_picture']
                        user.save()

                    # إنشاء سجل الموظف
                    HospitalStaff.objects.create(
                        user=user,
                        hospital=hospital,
                        role=form.cleaned_data['role'],
                        job_title=form.cleaned_data['job_title'],
                        status=form.cleaned_data['status'],
                        hire_date=form.cleaned_data['hire_date'],
                        notes=form.cleaned_data['notes'],
                    )

                    # إضافة رسالة نجاح مع بيانات تسجيل الدخول
                    success_message = f"""تم إضافة الموظف بنجاح. بيانات تسجيل الدخول:
                    البريد الإلكتروني: {email}
                    كلمة المرور: {form.cleaned_data['password']}
                    """
                    messages.success(request, success_message)
                    return redirect('/hospital/?section=staff_list')

            except Exception as e:
                messages.error(request, f"{_('حدث خطأ أثناء إضافة الموظف')}: {str(e)}")
        else:
            # إذا كان النموذج غير صالح، عرض الأخطاء
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StaffForm()

    context = {
        'roles': roles,
        'hospital': hospital,
        'form': form,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/add-staff.html', context)

@login_required
def edit_staff(request, staff_id):
    """تعديل بيانات موظف"""
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    hospital = get_object_or_404(Hospital, user=request.user)
    staff = get_object_or_404(HospitalStaff, id=staff_id, hospital=hospital)
    roles = StaffRole.objects.filter(hospital=hospital)
    permissions = StaffPermission.objects.all()
    additional_permissions = StaffAdditionalPermission.objects.filter(staff=staff)

    if request.method == 'POST':
        # استخدام نموذج تعديل الموظف بدلاً من نموذج إضافة الموظف
        form = StaffEditForm(request.POST, request.FILES, instance=staff.user, hospital=hospital)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # تحديث بيانات المستخدم
                    form.save()

                    # تحديث بيانات الموظف
                    staff.job_title = form.cleaned_data['job_title']
                    staff.status = form.cleaned_data['status']
                    staff.notes = form.cleaned_data['notes']
                    staff.role = form.cleaned_data['role']
                    staff.save()

                    # تحديث الصلاحيات الإضافية
                    StaffAdditionalPermission.objects.filter(staff=staff).delete()
                    for permission in permissions:
                        permission_value = request.POST.get(f'permission_{permission.id}')
                        if permission_value:
                            StaffAdditionalPermission.objects.create(
                                staff=staff,
                                permission=permission,
                                granted=(permission_value == 'grant')
                            )

                    messages.success(request, _("تم تحديث بيانات الموظف بنجاح"))
                    return redirect('/hospital/?section=staff_list')

            except Exception as e:
                messages.error(request, f"{_('حدث خطأ أثناء تحديث بيانات الموظف')}: {str(e)}")
        else:
            # إذا كان النموذج غير صالح، عرض الأخطاء
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # تهيئة نموذج تعديل الموظف ببيانات الموظف الحالية
        form = StaffEditForm(
            instance=staff.user,
            hospital=hospital,
            initial={
                'job_title': staff.job_title,
                'role': staff.role,
                'status': staff.status,
                'notes': staff.notes,
            }
        )

    context = {
        'staff': staff,
        'roles': roles,
        'permissions': permissions,
        'additional_permissions': {ap.permission_id: ap.granted for ap in additional_permissions},
        'hospital': hospital,
        'form': form,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/edit-staff.html', context)

@login_required
def delete_staff(request, staff_id):
    """حذف موظف"""
    # التحقق من أن المستخدم هو مدير مستشفى
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    # الحصول على المستشفى الخاص بالمستخدم
    hospital = get_object_or_404(Hospital, user=request.user)

    # الحصول على الموظف
    staff = get_object_or_404(HospitalStaff, id=staff_id, hospital=hospital)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # حذف حساب المستخدم (سيؤدي إلى حذف سجل الموظف تلقائيًا بسبب CASCADE)
                user = staff.user
                user.delete()

                messages.success(request, _("تم حذف الموظف بنجاح"))
                return redirect('/hospital/?section=staff_list')

        except Exception as e:
            messages.error(request, f"{_('حدث خطأ أثناء حذف الموظف')}: {str(e)}")
            return redirect('/hospital/?section=staff_list')

    context = {
        'staff': staff,
        'hospital': hospital,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/delete-staff.html', context)

# ===== إدارة الأدوار =====

@login_required
def role_list(request):
    """عرض قائمة الأدوار الوظيفية"""
    # التحقق من أن المستخدم هو مدير مستشفى
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    # الحصول على المستشفى الخاص بالمستخدم
    hospital = get_object_or_404(Hospital, user=request.user)

    # الحصول على قائمة الأدوار
    roles = StaffRole.objects.filter(hospital=hospital).prefetch_related('permissions')

    context = {
        'roles': roles,
        'hospital': hospital,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/role-list.html', context)

@login_required
def add_role(request):
    """إضافة دور وظيفي جديد"""
    # التحقق من أن المستخدم هو مدير مستشفى
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    # الحصول على المستشفى الخاص بالمستخدم
    hospital = get_object_or_404(Hospital, user=request.user)

    # الحصول على قائمة الصلاحيات
    permissions = StaffPermission.objects.all()

    if request.method == 'POST':
        # استخراج البيانات من النموذج
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_default = request.POST.get('is_default') == 'on'

        try:
            with transaction.atomic():
                # إنشاء الدور الوظيفي
                role = StaffRole.objects.create(
                    name=name,
                    description=description,
                    hospital=hospital,
                    is_default=is_default,
                )

                # إضافة الصلاحيات
                for permission in permissions:
                    if request.POST.get(f'permission_{permission.id}') == 'on':
                        role.permissions.add(permission)

                # إذا كان هذا الدور افتراضيًا، قم بإلغاء تعيين الأدوار الافتراضية الأخرى
                if is_default:
                    StaffRole.objects.filter(hospital=hospital, is_default=True).exclude(id=role.id).update(is_default=False)

                messages.success(request, _("تم إضافة الدور الوظيفي بنجاح"))
                return redirect('/hospital/?section=staff_list')
        except Exception as e:
            messages.error(request, f"{_('حدث خطأ أثناء إضافة الدور الوظيفي')}: {str(e)}")

    context = {
        'permissions': permissions,
        'hospital': hospital,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/add-role.html', context)









# ===== إدارة الأدوار =====





@login_required
def edit_role(request, role_id):
    """تعديل دور وظيفي"""
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    hospital = get_object_or_404(Hospital, user=request.user)
    role = get_object_or_404(StaffRole, id=role_id, hospital=hospital)
    permissions = StaffPermission.objects.all()
    role_permissions = role.permissions.all()

    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            try:
                with transaction.atomic():
                    role = form.save(commit=False)
                    role.save()

                    role.permissions.clear()
                    for permission in permissions:
                        if request.POST.get(f'permission_{permission.id}') == 'on':
                            role.permissions.add(permission)

                    if form.cleaned_data['is_default']:
                        StaffRole.objects.filter(hospital=hospital, is_default=True).exclude(id=role.id).update(is_default=False)

                    messages.success(request, _("تم تحديث الدور الوظيفي بنجاح"))
                    return redirect('/hospital/?section=staff_list')

            except Exception as e:
                messages.error(request, f"{_('حدث خطأ أثناء تحديث الدور الوظيفي')}: {str(e)}")

    else:
        form = RoleForm(instance=role)

    context = {
        'role': role,
        'permissions': permissions,
        'role_permissions': [p.id for p in role_permissions],
        'hospital': hospital,
        'form': form,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/edit-role.html', context)



@login_required
def delete_role(request, role_id):
    """حذف دور وظيفي"""
    # التحقق من أن المستخدم هو مدير مستشفى
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    # الحصول على المستشفى الخاص بالمستخدم
    hospital = get_object_or_404(Hospital, user=request.user)

    # الحصول على الدور الوظيفي
    role = get_object_or_404(StaffRole, id=role_id, hospital=hospital)

    # التحقق من عدم وجود موظفين مرتبطين بهذا الدور
    if HospitalStaff.objects.filter(role=role).exists():
        messages.error(request, _("لا يمكن حذف الدور الوظيفي لأنه مرتبط بموظفين"))
        return redirect('/hospital/?section=staff_list')

    if request.method == 'POST':
        try:
            role.delete()
            messages.success(request, _("تم حذف الدور الوظيفي بنجاح"))
            return redirect('/hospital/?section=staff_list')

        except Exception as e:
            messages.error(request, f"{_('حدث خطأ أثناء حذف الدور الوظيفي')}: {str(e)}")
            return redirect('/hospital/?section=staff_list')

    context = {
        'role': role,
        'hospital': hospital,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/delete-role.html', context)

# ===== إدارة الصلاحيات =====

@login_required
def permission_list(request):
    """عرض قائمة الصلاحيات"""
    # التحقق من أن المستخدم هو مدير مستشفى
    if request.user.user_type != 'hospital_manager':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    # الحصول على المستشفى الخاص بالمستخدم
    hospital = get_object_or_404(Hospital, user=request.user)

    # الحصول على قائمة الصلاحيات
    permissions = StaffPermission.objects.all()

    context = {
        'permissions': permissions,
        'hospital': hospital,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/staff/permission-list.html', context)


# ===== تغيير كلمة المرور عند أول تسجيل دخول =====

@login_required
def first_login_change_password(request):
    """تغيير كلمة المرور عند أول تسجيل دخول"""
    # التحقق من أن المستخدم هو موظف مستشفى
    if request.user.user_type != 'hospital_staff':
        messages.error(request, _("ليس لديك صلاحية الوصول إلى هذه الصفحة"))
        return redirect('hospitals:index')

    # الحصول على سجل الموظف
    try:
        staff = HospitalStaff.objects.get(user=request.user)
    except HospitalStaff.DoesNotExist:
        messages.error(request, _("لم يتم العثور على سجل موظف لحسابك"))
        return redirect('users:logout')

    # التحقق من أن هذا أول تسجيل دخول
    if not staff.is_first_login:
        return redirect('hospitals:index')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, _("كلمة المرور الجديدة وتأكيد كلمة المرور لا يتطابقان"))
            return redirect('hospital_staff:first_login_change_password')

        # تغيير كلمة المرور
        user = request.user
        user.set_password(new_password)
        user.save()

        # تحديث حالة أول تسجيل دخول
        staff.is_first_login = False
        staff.save()

        # تحديث جلسة المستخدم
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

        messages.success(request, _("تم تغيير كلمة المرور بنجاح"))
        return redirect('hospitals:index')

    return render(request, 'frontend/dashboard/hospitals/sections/staff/first_login_change_password.html')
