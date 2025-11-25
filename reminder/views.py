from django.shortcuts import render
from dateutil.relativedelta import relativedelta
# Create your views here.

import requests
import os
from rest_framework.views import APIView

from rest_framework.response import Response
from .models import Reminder
from .serializers import ReminderSerializer
from familymember.models import FamilyMember
from users.models import UserDetail
from django.utils import timezone
from datetime import datetime, timedelta
from .models import ExpoPushToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .utils import send_push_notification
from .cron import send_reminder_notifications
from insurance.models import Insurance
from vehicles.models import BluebookRenewal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .cron import send_reminder_notifications



class RemindersView(APIView):

    def get(self, request):
        print('called')
        user_detail = UserDetail.objects.get(user=request.user)
        member = FamilyMember.objects.get(user=user_detail)

        print('called1')
        family_members = FamilyMember.objects.filter(family=member.family)
        print('called 2')

        reminders = Reminder.objects.filter(family_member__in=family_members)
        print("called 3")
        print(reminders)
        serializer = ReminderSerializer(reminders, many=True)
        print(serializer.data)

        return Response(serializer.data)


@api_view(['POST'])
def ReminderTrigger(request):
        reminders_id = request.data.get('reminders_id')
        print(reminders_id)
        reminder = Reminder.objects.get(reminder_id=reminders_id)

        if reminder.is_active:
            reminder.is_active = False
            reminder.snoozed_until = timezone.now() + timezone.timedelta(days=1)
        else:
            reminder.is_active = True
            reminder.snoozed_until = None

        reminder.save()
        return Response({'message':'reminder changed.'})



@api_view(['POST'])
def SavenReminderConfig(request):
    try:
        reminder_id = request.data.get('reminder_id')
        new_freq = request.data.get('frequency')
        isSnoozeEnabled = request.data.get('isSnoozeEnabled')

        reminder = Reminder.objects.get(reminder_id=reminder_id)

        snooze_data = request.data.get('snooze', {})
        snooze_duration = None
        custom_snooze_date = None

        if snooze_data:
            snooze_duration = snooze_data.get('duration')
            custom_snooze_date = snooze_data.get('customDate')

        frequency_map = {
            "1d": timedelta(days=1),
            "3d": timedelta(days=3),
            "7d": timedelta(days=7),

            "14d": timedelta(days=14),
            "30d": timedelta(days=30),
        }

        new_window = frequency_map.get(new_freq, timedelta(days=1))

        # Get expiry date
        if reminder.target_type == "insurance":
            ins = reminder.vehicle.insurance_set.order_by('-expiry_date').first()
            expiry_date = ins.expiry_date if ins else None
        elif reminder.target_type == "bluebook":
            bb = reminder.vehicle.bluebook_renewals.order_by('-renewal_date').first()
            expiry_date = bb.renewal_date if bb else None
        else:
            expiry_date = None

        now = timezone.now()
        too_late = False

        if expiry_date:
            try:
                days_left = (expiry_date - now.date()).days
            except:
                days_left = (expiry_date - now).days

            if days_left < new_window.days:
                too_late = True

        reminder.frequency = new_freq

        # Only update frequency_updated_at if not too late
        if not too_late:
            reminder.frequency_updated_at = now


        if isSnoozeEnabled:
            reminder.is_active = False

            if snooze_duration == "custom" and custom_snooze_date:
                custom = datetime.fromisoformat(custom_snooze_date.replace("Z", "+00:00"))
                custom = custom.replace(
                    hour=now.hour,
                    minute=now.minute,
                    second=now.second,
                    microsecond=now.microsecond
                )
                reminder.snoozed_until = custom

            else:
                durations = {
                    '6h': timedelta(hours=6),
                    '1d': timedelta(days=1),
                    '2d': timedelta(days=2),
                    '3d': timedelta(days=3),
                    '7d': timedelta(days=7)
                }
                reminder.snoozed_until = now + durations.get(snooze_duration, timedelta(days=7))

        else:
            reminder.is_active = True
            reminder.snoozed_until = None

        reminder.save()

        return Response({
            "message": "Reminder updated successfully",
            "too_late": too_late,
            "frequency": reminder.frequency,
            "snoozed_until": reminder.snoozed_until
        })

    except Reminder.DoesNotExist:
        return Response({"error": "Reminder not found"}, status=404)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_token(request):
    token = request.data.get('token')
    userDetail = UserDetail.objects.get(user=request.user)
    ExpoPushToken.objects.update_or_create(user=userDetail, defaults={'token': token})
    return Response({"message": "Token saved successfully"})


@api_view(['POST'])
#test notification for request user
def test_notification(request):
    send_reminder_notifications()
    userDetail = UserDetail.objects.get(user=request.user)
    token = ExpoPushToken.objects.filter(user=userDetail).first()
    print(token)
    if token:
        send_push_notification(token.token, "Test Notification", "This is a test notification")
    return Response({"message": "Notification sent successfully"})




@api_view(['POST'])
def mark_renewed(request):

    target_type = request.data.get('target_type')
    id = request.data.get('id')

    if target_type == 'bluebook':
        bluebook_renewals = BluebookRenewal.objects.get(id=id)
        previous_renewal_date = bluebook_renewals.renewal_date

        bluebook_renewals.renewal_date = previous_renewal_date + relativedelta(years=1)

        bluebook_renewals.save()
    elif target_type == 'insurance':
        insurance = Insurance.objects.get(insurance_id=id)
        previous_renewal_date = insurance.expiry_date

        insurance.expiry_date = previous_renewal_date + relativedelta(years=1)
        insurance.save()
    else:
        return Response({"error": "Invalid target_type"}, status=400)
    return Response({"message": "Renewal date updated successfully"})




@csrf_exempt
@require_http_methods(["GET", "POST"])
def run_notifications_job(request):
    # 1. Check for the secret key in the URL's query parameters
    secret_key = request.GET.get('key')

    # 2. Compare it with the secret stored in environment variables
    if secret_key != os.environ.get('CRON_JOB_SECRET_KEY'):
        return JsonResponse({'status': 'unauthorized', 'message': 'Invalid key'}, status=401)

    # If the key is valid, run the job
    send_reminder_notifications()
    return JsonResponse({'status': 'success', 'message': 'Notification job executed.'})