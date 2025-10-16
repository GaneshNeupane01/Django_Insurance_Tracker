# cron.py
from .models import Reminder, ExpoPushToken
from .utils import send_push_notification
from datetime import datetime
from django.utils import timezone

def send_reminder_notifications():
    print('called send_reminder_notification func')
    reminders = Reminder.objects.all().order_by('frequency')
    print(reminders)

    now = timezone.now()
    for reminder in reminders:
        title = f"Reminder : {reminder.insurance.plan.vehicle_type}-{reminder.vehicle.plate_number}"
        if reminder.is_expired:
            print('expired')
            body = f"Insurance Expired for {reminder.insurance.plan.vehicle_type}-{reminder.vehicle.plate_number}"
        else:
            print('not expired')
            body = f"Insurance expires on {reminder.insurance.expiry_date}"
        if reminder.should_notify():
            print('should notify')

            token_obj = ExpoPushToken.objects.filter(user=reminder.family_member.user).first()
            print(token_obj.token)
            if token_obj:
                send_push_notification(
                    token_obj.token,
                    title,
                    body
                )
                reminder.last_sent = now
                reminder.save()
        else:
            print('shoudlnt notify')