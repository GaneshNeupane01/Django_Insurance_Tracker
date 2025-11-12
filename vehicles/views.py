from families.models import Family
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import VehicleSerializer
from familymember.models import FamilyMember
from vehicles.models import Vehicle,BluebookRenewal
from users.models import UserDetail
from reminder.models import Reminder
from insurance.models import Insurance,InsuranceCompany,InsurancePlan,VehicleTier
from vehicledocument.models import VehicleDocument
from django.utils import timezone

from datetime import datetime, timedelta
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
#from .ml.vehicle_predictor import predict_vehicle_type
import traceback
import logging

logger = logging.getLogger(__name__)

# Create your views here.
from datetime import datetime
from django.db import transaction
from .serializers import AddVehicleSerializer, EditVehicleSerializer
from insurance.models import InsuranceCompany, InsurancePlan

from cloudinary.uploader import destroy
from django.db.models import Q


import requests

HUGGINGFACE_SPACE_URL = "https://botinfinity-vehiclepredictor.hf.space/predict"

def send_image_to_huggingface(uploaded_file):
    files = {
        "file": (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
    }
    try:
        response = requests.post(HUGGINGFACE_SPACE_URL, files=files, timeout=40)
        response.raise_for_status()
        data = response.json()
        return data.get("label"), data.get("confidence")
    except requests.RequestException as e:
        print("Prediction service error:", e)
        return None, None



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
        print('called')
        serializer = AddVehicleSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data

        try:
            family_member = FamilyMember.objects.get(
                family_member_id=validated.get('family_member_id')
            )

            expiry_date_str = validated.get('insurance_renewal_date')
            bluebook_renewal_date_str = validated.get('bluebook_renewal_date')
            bluebook_renewal_date = datetime.fromisoformat(bluebook_renewal_date_str.replace("Z", "+00:00"))
            expiry_date = datetime.fromisoformat(expiry_date_str.replace("Z", "+00:00"))
            print('trying')
            #here we can call the func to predict type by passing validated image as argument
            uploaded_img = validated.get('vehicle_image')
            uploaded_img.seek(0)  # Reset file pointer before sending
            print("working till here")

            predicted_label, confidence = send_image_to_huggingface(uploaded_img)

            if predicted_label:
                print(f" Predicted Vehicle Type: {predicted_label} ({confidence*100:.2f}% confidence)")
            else:

                predicted_label = "Unknown"
                return Response(
                    {
                        "vehicleTypeError": "Please upload clear and valid vehicle image or try again.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            company = InsuranceCompany.objects.get(id=validated.get('company_id'))
            print(company)
            print(validated.get('payment_mode'))
            print(predicted_label)
            print('code reached here1')

            vehicle_category = validated.get("vehicle_category")
            if 'EV' in vehicle_category and validated.get("engine_wattage"):
                engine_wattage = validated.get("engine_wattage")
                engine_cc = None
            elif not 'EV' in vehicle_category and validated.get("engine_cc"):
                engine_cc = validated.get("engine_cc")
                engine_wattage = None
            else:
                return Response(
                    {"engine_cc": ["Please provide engine wattage or engine cc"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            is_ev = 'EV' in vehicle_category
            engine_value = engine_wattage if is_ev else engine_cc
            premium_amount = validated.get('premium_amount')

            if is_ev:
                vehicle_tier = VehicleTier.objects.get(vehicle_type=vehicle_category,min_engine_wattage__lte=engine_value,max_engine_wattage__gte=engine_value)

            else:
                vehicle_tier = VehicleTier.objects.get(vehicle_type=vehicle_category,min_engine_cc__lte=engine_value,max_engine_cc__gte=engine_value)

            try:
                plan = InsurancePlan.objects.get(
                    company=company,
                    vehicle_tier=vehicle_tier,
                )
            except InsurancePlan.DoesNotExist:
                print("no plan")
                return Response(
                    {
                        "planErrorDetail": "No matching insurance plan found! please upload correct vehicle image or company.",
                        "vehicleTypeError":"Please make sure vehicle image is valid and clear.Also ensure all provided info are valid.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if plan:
                print(plan)
            else:
                print("no plan")

            uploaded_img.seek(0)
            vehicle = Vehicle.objects.create(
                plate_number=validated.get('plate_number'),
                engine_cc=engine_cc,
                engine_wattage=engine_wattage,
                family_member=family_member,
                vehicle_image=uploaded_img
            )
            bluebook_renewal = BluebookRenewal.objects.create(
                vehicle=vehicle,
                renewal_date=bluebook_renewal_date
            )
            print(bluebook_renewal)
            insurance = Insurance.objects.create(
                vehicle=vehicle,
                plan=plan,
                expiry_date=expiry_date,
                amount=premium_amount,
            )
            print(insurance)

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
            print('created documents')
            now = timezone.now()

          #for insurance expiry creating reminder
            if (expiry_date - now) > timedelta(days=30):
                is_active = False
                snoozed_until = expiry_date - timedelta(days=30)
            else:
                is_active = True
                snoozed_until = None

            Reminder.objects.create(
                vehicle=vehicle,
                family_member=family_member,
                target_type="insurance",
                snoozed_until=snoozed_until,
                is_active=is_active,
                last_sent=None
            )
            print('created insurance renewal_date reminder')
            #for bluebook renewal creating reminder
            if (bluebook_renewal_date - now) > timedelta(days=30):
                is_active = False
                snoozed_until = bluebook_renewal_date - timedelta(days=30)
            else:
                is_active = True
                snoozed_until = None

            Reminder.objects.create(
                vehicle=vehicle,
                family_member=family_member,
                target_type="bluebook",
                snoozed_until=snoozed_until,
                is_active=is_active,
                last_sent=None
                )



            print("created bluebook_renewal reminder")
            return Response({"message": "Vehicle and related data saved"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()     # Prints the full traceback in console
            logger.error(traceback.format_exc())
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            reminder = Reminder.objects.get(vehicle=vehicle)
            reminder.family_member = family_member
            reminder.save()

            expiry_date_str = validated.get("insurance_renewal_date")
           # expiry_date = datetime.strptime(expiry_date_str, "%m/%d/%Y")
           # expiry_date = timezone.make_aware(expiry_date)


            vehicle_category = validated.get("vehicle_category")
            if 'EV' in vehicle_category and validated.get("engine_wattage"):
                engine_wattage = validated.get("engine_wattage")
                engine_cc = None
            elif not 'EV' in vehicle_category and validated.get("engine_cc"):
                engine_cc = validated.get("engine_cc")
                engine_wattage = None
            else:
                return Response(
                    {"engine_cc": ["Please provide engine wattage or engine cc"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            vehicle.engine_cc = engine_cc
            vehicle.engine_wattage = engine_wattage
            vehicle.plate_number = validated.get("plate_number")



            vehicle.family_member = family_member

            insurance = Insurance.objects.get(vehicle=vehicle)



            if validated.get("vehicle_image"):
                if vehicle.vehicle_image:
                    try:
                        destroy(vehicle.vehicle_image.public_id)
                    except Exception as e:
                        print(f"Error deleting old image from Cloudinary: {e}")


                vehicle.vehicle_image = validated.get("vehicle_image")

                uploaded_img = validated.get('vehicle_image')

                uploaded_img.seek(0)  # Reset file pointer before sending


                predicted_label, confidence = send_image_to_huggingface(uploaded_img)
                #predicted_label, confidence = predict_vehicle_type(uploaded_img)

                if predicted_label:
                    print(f" Predicted Vehicle Type: {predicted_label} ({confidence*100:.2f}% confidence)")

                else:
                    predicted_label = "Unknown"

                # Rewind again before saving to storage
                uploaded_img.seek(0)

            vehicle.save()


            # --- Update Insurance fields ---
            if expiry_date_str is not None:
                print(expiry_date_str)

                expiry_date = datetime.fromisoformat(expiry_date_str.replace("Z", "+00:00"))
                insurance.expiry_date = expiry_date

            company = InsuranceCompany.objects.get(id=validated.get("company_id"))
            print('this is ',company)

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

@api_view(['DELETE'])
def delete_vehicle(request, pk):
    try:
        vehicle = Vehicle.objects.get(pk=pk)

        # Delete image from Cloudinary if it exists
        if vehicle.vehicle_image:
            vehicle.vehicle_image.delete(save=False)

        vehicle.delete()

        return Response({'message': 'Vehicle deleted successfully'}, status=status.HTTP_200_OK)

    except Vehicle.DoesNotExist:
        return Response({'message': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)
