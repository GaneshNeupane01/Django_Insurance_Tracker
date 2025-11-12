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
        title = f"Reminder : {reminder.vehicle.insurance_set.plan.vehicle_tier.vehicle_type}-{reminder.vehicle.plate_number}"
        if reminder.is_expired:
            print('expired')
            if reminder.target_type == 'insurance':
                body = f"Insurance Expired for {reminder.vehicle.insurance_set.plan.vehicle_tier.vehicle_type}-{reminder.vehicle.plate_number}"
            elif reminder.target_type == 'bluebook':
                body = f'Bluebook Renewal Expired for {reminder.vehicle.plate_number}'
            else:
                return
        else:
            print('not expired')
            if reminder.target_type == 'insurance':
                body = f"Insurance expires on {reminder.vehicle.insurance_set.plan.vehicle_tier.vehicle_type}-{reminder.vehicle.plate_number} on {reminder.vehicle.insurance_set.expiry_date}"
            elif reminder.target_type == 'bluebook':
                body = f'Bluebook renewal on {reminder.vehicle.plate_number}'
            else:
                return

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