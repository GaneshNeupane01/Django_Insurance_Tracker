from django.shortcuts import render

# Create your views here.

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Reminder
from .serializers import ReminderSerializer
from familymember.models import FamilyMember
from users.models import UserDetail

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
