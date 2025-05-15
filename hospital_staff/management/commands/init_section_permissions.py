import os
from django.core.management.base import BaseCommand
from hospital_staff.models import StaffPermission
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = 'Initialize section visibility permissions for staff'

    def handle(self, *args, **options):
        # Define section permissions
        section_permissions = [
            # Dashboard sections
            {'name': _('عرض لوحة التحكم'), 'codename': 'view_dashboard', 'description': _('إمكانية مشاهدة لوحة التحكم الرئيسية')},
            
            # Hospital Management
            {'name': _('عرض إدارة المستشفى'), 'codename': 'view_hospital_management', 'description': _('إمكانية مشاهدة قسم إدارة المستشفى')},
            {'name': _('تعديل بيانات المستشفى'), 'codename': 'edit_hospital_data', 'description': _('إمكانية تعديل بيانات المستشفى')},
            
            # Staff Management
            {'name': _('عرض إدارة الموظفين'), 'codename': 'view_staff_management', 'description': _('إمكانية مشاهدة قسم إدارة الموظفين')},
            {'name': _('إضافة موظفين'), 'codename': 'add_staff', 'description': _('إمكانية إضافة موظفين جدد')},
            {'name': _('تعديل بيانات الموظفين'), 'codename': 'edit_staff', 'description': _('إمكانية تعديل بيانات الموظفين')},
            {'name': _('حذف الموظفين'), 'codename': 'delete_staff', 'description': _('إمكانية حذف الموظفين')},
            
            # Role Management
            {'name': _('عرض إدارة الأدوار'), 'codename': 'view_role_management', 'description': _('إمكانية مشاهدة قسم إدارة الأدوار الوظيفية')},
            {'name': _('إضافة أدوار وظيفية'), 'codename': 'add_role', 'description': _('إمكانية إضافة أدوار وظيفية جديدة')},
            {'name': _('تعديل الأدوار الوظيفية'), 'codename': 'edit_role', 'description': _('إمكانية تعديل الأدوار الوظيفية')},
            {'name': _('حذف الأدوار الوظيفية'), 'codename': 'delete_role', 'description': _('إمكانية حذف الأدوار الوظيفية')},
            
            # Doctors Management
            {'name': _('عرض إدارة الأطباء'), 'codename': 'view_doctors_management', 'description': _('إمكانية مشاهدة قسم إدارة الأطباء')},
            {'name': _('إضافة أطباء'), 'codename': 'add_doctor', 'description': _('إمكانية إضافة أطباء جدد')},
            {'name': _('تعديل بيانات الأطباء'), 'codename': 'edit_doctor', 'description': _('إمكانية تعديل بيانات الأطباء')},
            {'name': _('حذف الأطباء'), 'codename': 'delete_doctor', 'description': _('إمكانية حذف الأطباء')},
            
            # Appointments Management
            {'name': _('عرض إدارة المواعيد'), 'codename': 'view_appointments_management', 'description': _('إمكانية مشاهدة قسم إدارة المواعيد')},
            {'name': _('إضافة مواعيد'), 'codename': 'add_appointment', 'description': _('إمكانية إضافة مواعيد جديدة')},
            {'name': _('تعديل المواعيد'), 'codename': 'edit_appointment', 'description': _('إمكانية تعديل المواعيد')},
            {'name': _('حذف المواعيد'), 'codename': 'delete_appointment', 'description': _('إمكانية حذف المواعيد')},
            
            # Patients Management
            {'name': _('عرض إدارة المرضى'), 'codename': 'view_patients_management', 'description': _('إمكانية مشاهدة قسم إدارة المرضى')},
            {'name': _('إضافة مرضى'), 'codename': 'add_patient', 'description': _('إمكانية إضافة مرضى جدد')},
            {'name': _('تعديل بيانات المرضى'), 'codename': 'edit_patient', 'description': _('إمكانية تعديل بيانات المرضى')},
            {'name': _('حذف المرضى'), 'codename': 'delete_patient', 'description': _('إمكانية حذف المرضى')},
            
            # Payments Management
            {'name': _('عرض إدارة المدفوعات'), 'codename': 'view_payments_management', 'description': _('إمكانية مشاهدة قسم إدارة المدفوعات')},
            {'name': _('إضافة مدفوعات'), 'codename': 'add_payment', 'description': _('إمكانية إضافة مدفوعات جديدة')},
            {'name': _('تعديل المدفوعات'), 'codename': 'edit_payment', 'description': _('إمكانية تعديل المدفوعات')},
            
            # Reports
            {'name': _('عرض التقارير'), 'codename': 'view_reports', 'description': _('إمكانية مشاهدة قسم التقارير')},
            
            # Settings
            {'name': _('عرض الإعدادات'), 'codename': 'view_settings', 'description': _('إمكانية مشاهدة قسم الإعدادات')},
            {'name': _('تعديل الإعدادات'), 'codename': 'edit_settings', 'description': _('إمكانية تعديل إعدادات النظام')},
        ]
        
        # Create permissions
        created_count = 0
        for perm_data in section_permissions:
            perm, created = StaffPermission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['description']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created permission: {perm.name}'))
            else:
                # Update name and description if permission already exists
                perm.name = perm_data['name']
                perm.description = perm_data['description']
                perm.save()
                self.stdout.write(self.style.WARNING(f'Updated permission: {perm.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new permissions'))
