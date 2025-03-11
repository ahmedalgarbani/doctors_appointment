from __future__ import absolute_import, unicode_literals

# جعل التطبيق يتم تحميله مع Django
from .celery import app as celery_app

__all__ = ('celery_app',)
