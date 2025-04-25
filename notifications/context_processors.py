from .models import Notifications

def notifications(request):
    # تحقق من أن المستخدم مسجل الدخول
    if request.user.is_authenticated:

        notifications = Notifications.objects.filter(user=request.user).order_by('-send_time')

        # عدد الإشعارات غير المقروءة
        unread_notifications_count = notifications.filter(status='0').count()

        return {
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
        }
    else:
        # إذا كان المستخدم غير مسجل دخول، ارجع قاموس فارغ
        return {
            'notifications': [],
            'unread_notifications_count': 0,
        }
