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
from reminder.models import Reminder
from insurance.models import Insurance
from vehicledocument.models import VehicleDocument
from vehicles.models import Vehicle,BluebookRenewal
from rest_framework.decorators import api_view
from django.db import transaction


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





@api_view(['POST'])
def leave_and_create_family(request):
    user = request.user
    try:
        user_detail = UserDetail.objects.get(user=user)
        old_family_member = FamilyMember.objects.get(user=user_detail)
        old_family = old_family_member.family
    except FamilyMember.DoesNotExist:
        return Response({"error": "User is not part of any family"}, status=400)

    new_family_name = request.data.get('new_family_name')
    if not new_family_name:
        return Response({"error": "new_family_name is required"}, status=400)

    with transaction.atomic():
        vehicle_data = []
        for vehicle in old_family_member.vehicle_set.all():
            vehicle_data.append({
                "vehicle": vehicle,
                "reminders": list(vehicle.reminder_set.all()),
                "insurances": list(vehicle.insurance_set.all()),
                "docs": list(vehicle.vehicledocument_set.all()),
                "bluebook_renewals": list(vehicle.bluebook_renewals.all())
            })

        # if only one member
        old_family_has_only_this_user = old_family.familymember_set.count() == 1

        old_family_member.delete()

        new_family = Family.objects.create(name=new_family_name)
        new_family_member = FamilyMember.objects.create(
            user=user_detail,
            family=new_family,
            role="owner"
        )

        # Reassign all cached vehicles and their related objects
        for data in vehicle_data:
            vehicle = data["vehicle"]
            vehicle.family_member = new_family_member
            vehicle.save()

            for reminder in data["reminders"]:
                reminder.family_member = new_family_member
                reminder.save()

            for insurance in data["insurances"]:
                insurance.vehicle = vehicle
                insurance.save()
            for bluebook_renewal in data["bluebook_renewals"]:
                bluebook_renewal.vehicle = vehicle
                bluebook_renewal.save()

            for doc in data["docs"]:
                doc.vehicle = vehicle
                doc.save()

        # Delete old family if it had only this member
        if old_family_has_only_this_user:
            old_family.delete()

    return Response({"message": "Successfully left old family and created new family."}, status=200)

@api_view(['POST'])
def leave_and_join_family(request):
    user = request.user
    try:
        user_detail = UserDetail.objects.get(user=user)
        old_family_member = FamilyMember.objects.get(user=user_detail)
        old_family = old_family_member.family
    except FamilyMember.DoesNotExist:
        return Response({"error": "User is not part of any family"}, status=400)

    qr = request.data.get("qr_data")
    if not qr or not qr.startswith("family_join:"):
        return Response({"message": "Invalid QR code"}, status=400)

    parts = qr.split(":")
    if len(parts) != 3:
        return Response({"message": "Invalid QR code"}, status=400)

    family_id = parts[1]
    try:
        new_family = Family.objects.get(family_id=family_id)
    except Family.DoesNotExist:
        return Response({"message": "Family not found"}, status=404)

    with transaction.atomic():
        vehicle_data = []
        for vehicle in old_family_member.vehicle_set.all():
            vehicle_data.append({
                "vehicle": vehicle,
                "reminders": list(vehicle.reminder_set.all()),
                "insurances": list(vehicle.insurance_set.all()),
                "docs": list(vehicle.vehicledocument_set.all()),
                "bluebook_renewals": list(vehicle.bluebook_renewals.all())
            })

        old_family_has_only_this_user = old_family.familymember_set.count() == 1

        old_family_member.delete()

        new_family_member = FamilyMember.objects.create(
            user=user_detail,
            family=new_family,
            role="member"
        )

        for data in vehicle_data:
            vehicle = data["vehicle"]
            vehicle.family_member = new_family_member
            vehicle.save()

            for reminder in data["reminders"]:
                reminder.family_member = new_family_member
                reminder.save()

            for insurance in data["insurances"]:
                insurance.vehicle = vehicle
                insurance.save()

            for bluebook_renewal in data["bluebook_renewals"]:
                bluebook_renewal.vehicle = vehicle
                bluebook_renewal.save()

            for doc in data["docs"]:
                doc.vehicle = vehicle
                doc.save()

        if old_family_has_only_this_user:
            old_family.delete()

    return Response({"message": "Successfully left old family and joined new family."}, status=200)
