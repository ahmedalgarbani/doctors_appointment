from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Notifications
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def notifications_view(request):
    # Get base queryset
    notifications = Notifications.objects.filter(
        Q(user=request.user) | Q(sender=request.user)
    )

    # Apply filters
    search = request.GET.get('search')
    notification_type = request.GET.get('type')
    status = request.GET.get('status')

    if search:
        notifications = notifications.filter(
            Q(message__icontains=search) |
            Q(sender__username__icontains=search) |
            Q(user__username__icontains=search)
        )

    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)

    if status:
        notifications = notifications.filter(status=status)

    # Get all users for the send notification form
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)

    context = {
        'notifications': notifications,
        'users': users,
    }
    return render(request, 'notifications/notifications.html', context)

@login_required
def send_notification(request):
    if request.method == 'POST':
        recipients = request.POST.get('recipients')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type')

        try:
            if recipients == 'all':
                # Send to all users
                users = User.objects.filter(is_active=True).exclude(id=request.user.id)
                for user in users:
                    Notifications.objects.create(
                        sender=request.user,
                        user=user,
                        message=message,
                        notification_type=notification_type
                    )
            else:
                # Send to selected users
                user_ids = request.POST.getlist('users')
                for user_id in user_ids:
                    user = User.objects.get(id=user_id)
                    Notifications.objects.create(
                        sender=request.user,
                        user=user,
                        message=message,
                        notification_type=notification_type
                    )

            messages.success(request, 'Notification(s) sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')

    return redirect('notifications')

@login_required
def mark_as_read(request, notification_id):
    try:
        notification = Notifications.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        messages.success(request, 'Notification marked as read.')
    except Notifications.DoesNotExist:
        messages.error(request, 'Notification not found.')
    return redirect('notifications')

@login_required
def mark_as_unread(request, notification_id):
    try:
        notification = Notifications.objects.get(id=notification_id, user=request.user)
        notification.mark_as_unread()
        messages.success(request, 'Notification marked as unread.')
    except Notifications.DoesNotExist:
        messages.error(request, 'Notification not found.')
    return redirect('notifications')