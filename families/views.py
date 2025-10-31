from django.shortcuts import render
import qrcode
import io
import base64
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
            if family_name == "" or family_name == None:
                family_name = f"{userDetail.user.last_name} Family"
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


class GetFamilyQR(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        userDetail = UserDetail.objects.get(user=request.user)
        family = FamilyMember.objects.get(user=userDetail).family
        if not family:
            return Response({"message":"Family not found"},status=404)
        if not family.qr_code:
            family.qr_code = f"family_join:{family.family_id}:{family.name}"
            family.save()

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(family.qr_code)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer,format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        print(img_str,"returned qr image")

        return Response({"qr_code":img_str},status=200)


class JoinQR(APIView):
    def post(self,request):
        qr_data = request.data.get("qr_data")
        userDetail = UserDetail.objects.get(user=request.user)
        if not qr_data.startswith("family_join:"):
            return Response({"message":"Invalid QR code"},status=400)
        qr_data = qr_data.split(":")
        if len(qr_data) != 3:
            return Response({"message":"Invalid QR code"},status=400)
        family_id = qr_data[1]

        if(Family.objects.get(family_id=family_id)):
                family = Family.objects.get(family_id=family_id)
                FamilyMember.objects.create(user=userDetail, family=family, role="member")
        else:
                return Response({"message":"Family not found"},status=404)

        return Response({"message":"Family added successfully"},status=200)



