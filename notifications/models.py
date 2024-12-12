from django.db import models

class Notifications(models.Model):
    sender = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='sent_notifications')
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField()
    send_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    notification_type = models.CharField(max_length=50)
