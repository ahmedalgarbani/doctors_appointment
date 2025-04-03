from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Booking
from notifications.models import Notifications

@shared_task
def send_appointment_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)
    bookings = Booking.objects.filter(appointment_date__date=tomorrow)

    for booking in bookings:
        Notifications.objects.create(
            user=booking.patient,  # إرسال الإشعار للمريض
            title="تذكير بالموعد الطبي",
            message=f"لديك موعد مع الدكتور {booking.doctor} في مستشفى {booking.hospital} غداً {booking.appointment_date} الساعة {booking.appointment_time}.",
            notification_type="reminder"
        )
    return f"تم إرسال {bookings.count()} إشعاراً للمواعيد القادمة."

from celery import shared_task

# مثال على مهمة بسيطة
@shared_task
def send_reminder_email(user_id):
    # الكود الخاص بإرسال تذكير بالبريد الإلكتروني
    print(f"Sending reminder email to user {user_id}")

