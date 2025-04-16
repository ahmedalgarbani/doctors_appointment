from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import HospitalStaff, StaffRole, StaffPermission

User = get_user_model()

class StaffForm(forms.ModelForm):
    """نموذج إضافة موظف جديد"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("الاسم الأول")
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("الاسم الأخير")
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("اسم المستخدم")
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label=_("البريد الإلكتروني")
    )
    mobile_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("رقم الهاتف")
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_("كلمة المرور")
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_("تأكيد كلمة المرور")
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label=_("الصورة الشخصية")
    )

    class Meta:
        model = HospitalStaff
        fields = ['job_title', 'role', 'hire_date', 'status', 'notes']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', _("كلمات المرور غير متطابقة"))

        return cleaned_data


class StaffEditForm(forms.ModelForm):
    """نموذج تعديل بيانات موظف"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("الاسم الأول")
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("الاسم الأخير")
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label=_("البريد الإلكتروني")
    )
    mobile_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("رقم الهاتف")
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label=_("الصورة الشخصية")
    )
    job_title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("المسمى الوظيفي")
    )
    role = forms.ModelChoiceField(
        queryset=StaffRole.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("الدور الوظيفي")
    )
    status = forms.ChoiceField(
        choices=HospitalStaff.STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("الحالة")
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label=_("ملاحظات")
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super(StaffEditForm, self).__init__(*args, **kwargs)
        if hospital:
            self.fields['role'].queryset = StaffRole.objects.filter(hospital=hospital)

class RoleForm(forms.ModelForm):
    """نموذج إضافة/تعديل دور وظيفي"""
    class Meta:
        model = StaffRole
        fields = ['name', 'description', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PermissionForm(forms.ModelForm):
    """نموذج إضافة/تعديل صلاحية"""
    class Meta:
        model = StaffPermission
        fields = ['name', 'codename', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'codename': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
