from notifications.models import Notifications

def get_user_notifications(user):
    notifications = Notifications.objects.filter(user=user)
    unread_notifications_count = notifications.filter(status='0').count()
    return notifications, unread_notifications_count

def get_notifications_sended_from(user):
    """
        get all notifications that hospital sended
    """
    notifications = Notifications.objects.filter(sender=user, is_active=True).order_by('-send_time')
    return notifications
