# cron.py
from .models import Reminder, ExpoPushToken
from .utils import send_push_notification
from datetime import datetime
from django.utils import timezone
from familymember.models import FamilyMember
from insurance.models import Insurance
from vehicles.models import BluebookRenewal



def send_reminder_notifications():
    print('called send_reminder_notification func')
    reminders = Reminder.objects.all().order_by('frequency')
    print(reminders)

    now = timezone.now()
    for reminder in reminders:
        insurance = (
            Insurance.objects.select_related('plan__vehicle_tier')
            .filter(vehicle=reminder.vehicle)
            .order_by('-expiry_date')
            .first()
        )
        bluebook = (
            BluebookRenewal.objects.filter(vehicle=reminder.vehicle)
            .order_by('-renewal_date')
            .first()
        )

        vehicle_type = (
            insurance.plan.vehicle_tier.vehicle_type
            if insurance and getattr(insurance, 'plan', None) and getattr(insurance.plan, 'vehicle_tier', None)
            else 'Vehicle'
        )
        title = f"Reminder : {vehicle_type}-{reminder.vehicle.plate_number}"

        if reminder.is_expired:
            continue

        if reminder.target_type == 'insurance':
            if not insurance:
                continue
            body = (
                f"Insurance expires on {vehicle_type}-"
                f"{reminder.vehicle.plate_number} on {insurance.expiry_date}"
            )
        elif reminder.target_type == 'bluebook':
            if not bluebook:
                continue
            body = (
                f'Bluebook renewal for {reminder.vehicle.plate_number} '
                f'on {bluebook.renewal_date}'
            )
        else:
            continue
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