from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class HospitalStaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospital_staff'
    verbose_name = _('إدارة موظفي المستشفى')
