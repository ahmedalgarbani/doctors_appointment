from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from hospital_staff.models import StaffPermission

class Command(BaseCommand):
    help = 'إنشاء الصلاحيات الافتراضية لموظفي المستشفى'
    
    def handle(self, *args, **kwargs):
        # قائمة الصلاحيات الافتراضية
        default_permissions = [
            # صلاحيات إدارة الأطباء
            {
                'name': _('إدارة الأطباء'),
                'codename': 'manage_doctors',
                'description': _('إضافة وتعديل وحذف الأطباء')
            },
            {
                'name': _('عرض الأطباء'),
                'codename': 'view_doctors',
                'description': _('عرض قائمة الأطباء وتفاصيلهم')
            },
            
            # صلاحيات إدارة المواعيد
            {
                'name': _('إدارة المواعيد'),
                'codename': 'manage_appointments',
                'description': _('إضافة وتعديل وحذف المواعيد')
            },
            {
                'name': _('عرض المواعيد'),
                'codename': 'view_appointments',
                'description': _('عرض قائمة المواعيد وتفاصيلها')
            },
            
            # صلاحيات إدارة الحجوزات
            {
                'name': _('إدارة الحجوزات'),
                'codename': 'manage_bookings',
                'description': _('إضافة وتعديل وحذف الحجوزات')
            },
            {
                'name': _('عرض الحجوزات'),
                'codename': 'view_bookings',
                'description': _('عرض قائمة الحجوزات وتفاصيلها')
            },
            
            # صلاحيات إدارة المدفوعات
            {
                'name': _('إدارة المدفوعات'),
                'codename': 'manage_payments',
                'description': _('إضافة وتعديل وحذف المدفوعات')
            },
            {
                'name': _('عرض المدفوعات'),
                'codename': 'view_payments',
                'description': _('عرض قائمة المدفوعات وتفاصيلها')
            },
            {
                'name': _('التحقق من المدفوعات'),
                'codename': 'verify_payments',
                'description': _('التحقق من المدفوعات وتأكيدها')
            },
            
            # صلاحيات إدارة المرضى
            {
                'name': _('إدارة المرضى'),
                'codename': 'manage_patients',
                'description': _('إضافة وتعديل وحذف المرضى')
            },
            {
                'name': _('عرض المرضى'),
                'codename': 'view_patients',
                'description': _('عرض قائمة المرضى وتفاصيلهم')
            },
            
            # صلاحيات إدارة التقارير
            {
                'name': _('عرض التقارير'),
                'codename': 'view_reports',
                'description': _('عرض التقارير والإحصائيات')
            },
            
            # صلاحيات إدارة الإشعارات
            {
                'name': _('إدارة الإشعارات'),
                'codename': 'manage_notifications',
                'description': _('إرسال وإدارة الإشعارات')
            },
        ]
        
        # إنشاء الصلاحيات
        created_count = 0
        for perm in default_permissions:
            permission, created = StaffPermission.objects.get_or_create(
                codename=perm['codename'],
                defaults={
                    'name': perm['name'],
                    'description': perm['description']
                }
            )
            
            if created:
                created_count += 1
            else:
                # تحديث الاسم والوصف إذا تغيرت
                if permission.name != perm['name'] or permission.description != perm['description']:
                    permission.name = perm['name']
                    permission.description = perm['description']
                    permission.save()
        
        self.stdout.write(self.style.SUCCESS(f'تم إنشاء {created_count} صلاحية جديدة'))
