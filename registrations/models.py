from django.db import models

class RegistrationRequests(models.Model):
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    attached_documents = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(blank=True, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)
