
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
    ALLOWED_DOC_TYPES = ['insurance', 'license', 'registration','other']

    def get(self, request):

        user_detail = UserDetail.objects.get(user=request.user)
        member = FamilyMember.objects.get(user=user_detail)


        family_members = FamilyMember.objects.filter(family=member.family)

        vehicles = Vehicle.objects.filter(family_member__in=family_members)

        serializer = VehicleSerializer(vehicles, many=True)
        print(serializer.data)

        return Response(serializer.data)


    def post(self, request):
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

            insurance = Insurance.objects.create(
                vehicle=vehicle,
                insurance_company=validated.get('insurance_company'),
                expiry_date=expiry_date,
                payment_mode=validated.get('payment_mode'),
                amount=validated.get('premium_amount')
            )

            # Handle multiple documents here
            documents = request.FILES.getlist('documents')
            doc_types = request.data.getlist('doc_types')

            if len(documents) != len(doc_types):
                return Response(
                    {"detail": "Mismatch between documents and document types count"},
                    status=status.HTTP_400_BAD_REQUEST
                )



            for doc, doc_type in zip(documents, doc_types):
                VehicleDocument.objects.create(
                    vehicle=vehicle,
                    doc_type=doc_type,
                    image=doc
                )

            Reminder.objects.create(
                vehicle=vehicle,
                family_member=family_member,
                insurance=insurance,
                target_type="insurance",
                reminder_date=timezone.now(),
                snoozed_until=None,
                is_active=True
            )

            return Response({"message": "Vehicle and related data saved"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EditVehicleView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AddVehicleSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data

        try:
            vehicle_id = validated.get("vehicle_id")
            vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)


            family_member = FamilyMember.objects.get(
                family_member_id=validated.get("family_member_id")
            )

            # Convert expiry date
            expiry_date_str = validated.get("insurance_renewal_date")
            expiry_date = datetime.strptime(expiry_date_str, "%m/%d/%Y")
            expiry_date = timezone.make_aware(expiry_date)

            # --- Update Vehicle fields ---
            vehicle.name = validated.get("name")
            vehicle.plate_number = validated.get("plate_number")
            vehicle.engine_cc = validated.get("engine_cc")
            vehicle.family_member = family_member

            if validated.get("vehicle_image"):  # only update if new image provided
                vehicle.vehicle_image = validated.get("vehicle_image")

            vehicle.save()

            # --- Update Insurance fields ---
            insurance = Insurance.objects.get(vehicle=vehicle)
            insurance.insurance_company = validated.get("insurance_company")
            insurance.expiry_date = expiry_date
            insurance.payment_mode = validated.get("payment_mode")
            insurance.amount = validated.get("premium_amount")
            insurance.save()

            return Response(
                {"message": "Vehicle and related data updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Vehicle not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )