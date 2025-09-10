from django.shortcuts import render

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny,IsAuthenticated
from families.models import Family
from familymember.models import FamilyMember
from users.models import UserDetail


class AddFamily(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        family_action = request.data.get("family_action")
        userDetail = UserDetail.objects.get(user=request.user)
        if family_action == "create":
            family_name = request.data.get("family_name")
            family = Family.objects.create(name=family_name)
            FamilyMember.objects.create(user=userDetail, family=family, role="owner")
        else:
            family_id = request.data.get("family_id")
            if(Family.objects.get(family_id=family_id)):
                family = Family.objects.get(family_id=family_id)
                FamilyMember.objects.create(user=userDetail, family=family, role="member")
            else:
                return Response({"message":"Family not found"},status=404)

        return Response({"message":"Family added successfully"},status=200)




