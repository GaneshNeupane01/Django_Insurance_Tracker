
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
        data = request.data
        print(data)
        print("called api")
        family_member = FamilyMember.objects.get(family_member_id=data.get('family_member_id'))

        expiry_date_str = data.get("insurance_renewal_date")
        expiry_date = datetime.strptime(expiry_date_str, "%m/%d/%Y")
        expiry_date = timezone.make_aware(expiry_date)

        vehicle = Vehicle.objects.create(
            name=data.get('name'),
            plate_number=data.get('plate_number'),
            engine_cc=data.get('engine_cc'),
            family_member=family_member
        )

        insurance = Insurance.objects.create(
            vehicle=vehicle,
            insurance_company=data.get('insurance_company'),
            expiry_date=expiry_date,
            payment_mode=data.get('payment_mode'),
            amount=data.get('premium_amount')
        )

        document = VehicleDocument.objects.create(
            vehicle=vehicle,
            doc_type=data.get('vehicle_document_type'),
            image=data.get('image')
        )


        #reminders creation later

        return Response({"message": "Vehicle and related data saved"}, status=status.HTTP_201_CREATED)

