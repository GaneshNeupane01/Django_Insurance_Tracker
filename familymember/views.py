from django.shortcuts import render
from familymember.models import FamilyMember
from familymember.serializers import FamilyMemberSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny,IsAuthenticated
from users.models import UserDetail


# Create your views here.

class FamilyMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserDetail.objects.get(user=request.user)
        family = FamilyMember.objects.filter(user=user).first().family
        family_members = FamilyMember.objects.filter(family=family)
        serializer = FamilyMemberSerializer(family_members, many=True)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request):
        muser= User.objects.get(username=request.data.get('username'))
        memberUser = UserDetail.objects.get(user=muser)
        user = UserDetail.objects.get(user=request.user)
        family = FamilyMember.objects.filter(user=user).first().family
        family_member = FamilyMember.objects.create(user=memberUser, family=family,role='member')
        #serializer = FamilyMemberSerializer(family_member)
        return Response({'message': 'Family member added successfully'})



