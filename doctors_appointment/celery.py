from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# تحديد إعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors_appointment.settings')

# إنشاء تطبيق Celery
app = Celery('doctors_appointment')

# استخدام إعدادات Django في Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# تحميل المهام من التطبيقات المثبتة
app.autodiscover_tasks()

