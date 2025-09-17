
from families.models import Family
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import VehicleSerializer
from familymember.models import FamilyMember
from vehicles.models import Vehicle
from users.models import UserDetail
from reminder.models import Reminder
from insurance.models import Insurance
from vehicledocument.models import VehicleDocument
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
from datetime import datetime
from django.db import transaction
from .serializers import AddVehicleSerializer




class VehicleListView(APIView):
    print('api called successfully')
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):

        user_detail = UserDetail.objects.get(user=request.user)
        member = FamilyMember.objects.get(user=user_detail)


        family_members = FamilyMember.objects.filter(family=member.family)

        vehicles = Vehicle.objects.filter(family_member__in=family_members)

        serializer = VehicleSerializer(vehicles, many=True)
        print(serializer.data)

        return Response(serializer.data)


    def post(self, request):
        print("called api")
        serializer = AddVehicleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data

        try:

                family_member = FamilyMember.objects.get(
                    family_member_id=validated.get('family_member_id')
                )

                expiry_date_str = validated.get('insurance_renewal_date')
                expiry_date = datetime.strptime(expiry_date_str, "%m/%d/%Y")
                expiry_date = timezone.make_aware(expiry_date)

                vehicle = Vehicle.objects.create(
                    name=validated.get('name'),
                    plate_number=validated.get('plate_number'),
                    engine_cc=validated.get('engine_cc'),
                    family_member=family_member,
                    vehicle_image=validated.get('vehicle_image')
                )

                Insurance.objects.create(
                    vehicle=vehicle,
                    insurance_company=validated.get('insurance_company'),
                    expiry_date=expiry_date,
                    payment_mode=validated.get('payment_mode'),
                    amount=validated.get('premium_amount')
                )

                VehicleDocument.objects.create(
                    vehicle=vehicle,
                    doc_type=validated.get('vehicle_document_type'),
                    image=validated.get('image')
                )
                Reminder.objects.create(
                     vehicle=vehicle,
                     family_member=family_member,
                     insurance=insurance,
                     target_type="insurance",
                     reminder_date=timezone.now(),
                     snoozed_until=None,
                     s_active=True
                )

                return Response({"message": "Vehicle and related data saved"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)