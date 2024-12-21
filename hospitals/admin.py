from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from .models import Hospital, HospitalAccountRequest, City, PhoneNumber

User = get_user_model()

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status') 
    prepopulated_fields = {'slug': ('name',)} 
    list_filter = ('status',)  
    search_fields = ('name', 'slug')  

@admin.register(HospitalAccountRequest)
class HospitalAccountRequestAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'manager_full_name', 'manager_email', 'status', 'created_at', 'view_documents']
    list_filter = ['status', 'created_at']
    search_fields = ['hospital_name', 'manager_full_name', 'manager_email']
    readonly_fields = ['created_at', 'created_by']
    actions = ['approve_requests', 'reject_requests']

    def view_documents(self, obj):
        links = []
        if obj.commercial_record:
            links.append(format_html('<a href="{}" target="_blank">السجل التجاري</a>', obj.commercial_record.url))
        if obj.medical_license:
            links.append(format_html('<a href="{}" target="_blank">الترخيص الطبي</a>', obj.medical_license.url))
        return format_html(' | '.join(links))
    view_documents.short_description = 'المستندات'

    def approve_requests(self, request, queryset):
        for hospital_request in queryset.filter(status='pending'):
            # إنشاء حساب مستخدم جديد لمدير المستشفى
            user = User.objects.create_user(
                username=hospital_request.manager_email,  # استخدام البريد الإلكتروني كاسم مستخدم
                email=hospital_request.manager_email,
                first_name=hospital_request.manager_full_name.split(' ')[0],
                last_name=' '.join(hospital_request.manager_full_name.split(' ')[1:]),
                user_type='hospital_manager',
                mobile_number=hospital_request.manager_phone,
            )
            # استخدام كلمة المرور المخزنة
            user.set_password(hospital_request.manager_password)
            user.save()

            # إنشاء سجل المستشفى
            hospital = Hospital.objects.create(
                name=hospital_request.hospital_name,
                location=hospital_request.hospital_location,
                hospital_manager_id=user.id
            )

            # تحديث حالة الطلب
            hospital_request.status = 'approved'
            hospital_request.reviewed_by = request.user
            hospital_request.save()

            # إرسال بريد إلكتروني بمعلومات تسجيل الدخول
            subject = 'تمت الموافقة على طلب تسجيل المستشفى'
            message = f'''مرحباً {hospital_request.manager_full_name}،
            
            تمت الموافقة على طلب تسجيل المستشفى الخاص بكم. يمكنكم الآن تسجيل الدخول باستخدام المعلومات التالية:
            
            اسم المستخدم: {user.username}
            كلمة المرور: {hospital_request.manager_password}
            
            يرجى تغيير كلمة المرور بعد تسجيل الدخول لأول مرة.
            '''
            try:
                user.email_user(subject, message)
            except Exception as e:
                self.message_user(request, f"تم إنشاء الحساب ولكن فشل إرسال البريد الإلكتروني: {str(e)}")

        self.message_user(request, f"تمت الموافقة على {queryset.count()} طلب/طلبات بنجاح")

    approve_requests.short_description = "الموافقة على الطلبات المحددة"

    def reject_requests(self, request, queryset):
        queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user
        )
        self.message_user(request, f"تم رفض {queryset.count()} طلب/طلبات")
    reject_requests.short_description = "رفض الطلبات المحددة"

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'hospital_manager_id', 'created_at')
    search_fields = ('name', 'location')
    ordering = ('-created_at',)

@admin.register(HospitalDetail)
class HospitalDetailAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'specialty', 'status', 'show_at_home')
    search_fields = ('hospital__name', 'specialty__name')
    list_filter = ('status', 'show_at_home')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'phone_type', 'hospital')
    search_fields = ('number', 'hospital__name')
    list_filter = ('phone_type',)
