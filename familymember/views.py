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
        username = request.data.get('username')
        if not username:
            return Response({'message': 'Username is required','flag':'error'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            muser= User.objects.get(username=request.data.get('username'))

        except:
            return Response({'message': 'User not found','flag':'error'})
        memberUser = UserDetail.objects.get(user=muser)
        user = UserDetail.objects.get(user=request.user)
        family = FamilyMember.objects.filter(user=user).first().family
        if FamilyMember.objects.filter(user=memberUser, family=family).exists():
            return Response({'message': 'User is already a family member'}, status=status.HTTP_409_CONFLICT)

        family_member = FamilyMember.objects.create(user=memberUser, family=family,role='member')
        #serializer = FamilyMemberSerializer(family_member)
        return Response({'message': 'Family member added successfully','flag':'success'})



