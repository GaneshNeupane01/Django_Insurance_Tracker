# cron.py
from .models import Reminder, ExpoPushToken
from .utils import send_push_notification
from datetime import datetime
from django.utils import timezone
from familymember.models import FamilyMember

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
            family = reminder.family_member.family
            all_family_members = FamilyMember.objects.filter(family=family)
            for family_member in all_family_members:
                token_obj = ExpoPushToken.objects.filter(user=family_member.user).first()
                if token_obj:
                    send_push_notification(
                        token_obj.token,
                        title,
                        body
                    )
            reminder.last_sent = now
            reminder.save()
        else:
            print('shouldnt notify')