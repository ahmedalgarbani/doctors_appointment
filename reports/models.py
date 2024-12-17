from django.db import models
from django.conf import settings

class Reports(models.Model):
    report_type = models.CharField(max_length=50)
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
