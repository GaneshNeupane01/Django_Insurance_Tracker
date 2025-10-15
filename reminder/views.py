from django.shortcuts import render

# Create your views here.

import requests
from rest_framework.views import APIView

from rest_framework.response import Response
from .models import Reminder
from .serializers import ReminderSerializer
from familymember.models import FamilyMember
from users.models import UserDetail
from django.utils import timezone
from datetime import datetime
from .models import ExpoPushToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .utils import send_push_notification

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
        frequency = request.data.get('frequency')
        isSnoozeEnabled = request.data.get('isSnoozeEnabled')

        print("this is id ", reminder_id)
        print("this is frequency ", frequency)

        snooze_data = request.data.get('snooze')
        snooze_duration = None
        custom_snooze_date = None

        if snooze_data:
            print(snooze_data)
            snooze_duration = snooze_data.get('duration')
            print(snooze_duration)
            custom_snooze_date = snooze_data.get('customDate')
            print(custom_snooze_date)

        reminder = Reminder.objects.get(reminder_id=reminder_id)
        reminder.frequency = frequency

        if isSnoozeEnabled:
            reminder.is_active = False

            if snooze_duration == 'custom' and custom_snooze_date:
                # Adjust format depending on what frontend sends
               # custom_snooze_date = datetime.fromisoformat(custom_snooze_date)
                custom_snooze_date = datetime.fromisoformat(custom_snooze_date.replace("Z", "+00:00"))

               # custom_snooze_date = timezone.make_aware(custom_snooze_date)
                reminder.snoozed_until = custom_snooze_date
            elif snooze_duration == '6h':
                reminder.snoozed_until = timezone.now() + timezone.timedelta(hours=6)
            elif snooze_duration == '1d':
                reminder.snoozed_until = timezone.now() + timezone.timedelta(days=1)
            elif snooze_duration == '2d':
                reminder.snoozed_until = timezone.now() + timezone.timedelta(days=2)
            elif snooze_duration == '3d':
                reminder.snoozed_until = timezone.now() + timezone.timedelta(days=3)
            elif snooze_duration == '7d':
                reminder.snoozed_until = timezone.now() + timezone.timedelta(days=7)
            else:
                reminder.snoozed_until = timezone.now() + timezone.timedelta(days=7)
        else:
            reminder.is_active = True
            reminder.snoozed_until = None

        reminder.save()

        return Response({
            "message": "Reminder updated successfully",
            "reminder_id": reminder_id,
            "frequency": frequency,
            "snoozed_until": reminder.snoozed_until
        }, status=200)

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
    userDetail = UserDetail.objects.get(user=request.user)
    token = ExpoPushToken.objects.filter(user=userDetail).first()
    if token:
        send_push_notification(token.token, "Test Notification", "This is a test notification")
    return Response({"message": "Notification sent successfully"})