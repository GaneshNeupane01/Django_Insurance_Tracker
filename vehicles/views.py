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
from .ml.vehicle_predictor import predict_vehicle_type

# Create your views here.
from datetime import datetime
from django.db import transaction
from .serializers import AddVehicleSerializer, EditVehicleSerializer
from insurance.models import InsuranceCompany, InsurancePlan

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

            #here we can call the func to predict type by passing validated image as argument
            uploaded_img = validated.get('vehicle_image')
            predicted_label, confidence = predict_vehicle_type(uploaded_img)

            if predicted_label:
                print(f" Predicted Vehicle Type: {predicted_label} ({confidence*100:.2f}% confidence)")
            else:
                predicted_label = "Unknown"
            company = InsuranceCompany.objects.get(id=validated.get('company_id'))
            print(company)
            print(validated.get('payment_mode'))
            print(predicted_label)
            print('code reached here')
            # Normalize labels to match InsurancePlan choices/values

            normalized_payment_mode = str(validated.get('payment_mode', '')).strip().lower()

            try:
                plan = InsurancePlan.objects.get(
                    company=company,
                    vehicle_type=predicted_label,
                    payment_mode=normalized_payment_mode,
                )
            except InsurancePlan.DoesNotExist:
                print("no plan")
                return Response(
                    {
                        "planErrorDetail": "No matching insurance plan found! please upload correct vehicle image or company.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            print('code never reached here giving internel server error')
            if plan:
                print(plan)
            else:
                print("no plan")
            vehicle = Vehicle.objects.create(
                name=validated.get('name'),
                plate_number=validated.get('plate_number'),
                engine_cc=validated.get('engine_cc'),
                family_member=family_member,
                vehicle_image=validated.get('vehicle_image')
            )

            insurance = Insurance.objects.create(
                vehicle=vehicle,
                plan=plan,
             #   insurance_company=validated.get('insurance_company'),

                expiry_date=expiry_date,
            #    payment_mode=validated.get('payment_mode'),
            #    amount=validated.get('premium_amount')
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

#we can make a function to predict type here ??
class EditVehicleView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EditVehicleSerializer(data=request.data)
        print('test1')
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print('test2')
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
           # vehicle.name = validated.get("name")
            vehicle.plate_number = validated.get("plate_number")
            vehicle.engine_cc = validated.get("engine_cc")
            vehicle.family_member = family_member

            insurance = Insurance.objects.get(vehicle=vehicle)
            vehicle_type = insurance.plan.vehicle_type
            print(vehicle_type)

            if validated.get("vehicle_image"):  # only update if new image provided
                vehicle.vehicle_image = validated.get("vehicle_image")

                uploaded_img = validated.get('vehicle_image')
                predicted_label, confidence = predict_vehicle_type(uploaded_img)

                if predicted_label:
                    print(f" Predicted Vehicle Type: {predicted_label} ({confidence*100:.2f}% confidence)")
                    vehicle_type = predicted_label
                else:
                    predicted_label = "Unknown"

            vehicle.save()


            # --- Update Insurance fields ---

            company = InsuranceCompany.objects.get(id=validated.get("company_id"))
            print('this is ',company)


            insurance.expiry_date = expiry_date
            print(validated.get("payment_mode"))
            plan = InsurancePlan.objects.get( company=company, vehicle_type=vehicle_type, payment_mode=validated.get("payment_mode"))
            insurance.plan = plan
            print(plan)
           # insurance.amount = validated.get("premium_amount")
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