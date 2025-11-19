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

            company = InsuranceCompany.objects.get(id=validated.get('company_id'))
            print(company)


            print('code reached here1')
            is_ev = validated.get('is_ev')
            is_ev = is_ev.lower() == "true" if is_ev else False
            vehicle_type = validated.get("vehicle_type")
            if is_ev and validated.get("engine_wattage"):
                engine_wattage = validated.get("engine_wattage")
                engine_cc = None
                if vehicle_type == "Car":
                    vehicle_category = "Car (EV)"
                elif vehicle_type == "Motorcycle":
                    vehicle_category = "Motorcycle (EV)"
                else:
                    return JsonResponse({"error": "Unsupported vehicle_type."}, status=400)
                vehicle_tier = VehicleTier.objects.get(vehicle_type=vehicle_category,min_engine_wattage__lte=engine_wattage,max_engine_wattage__gte=engine_wattage)
            elif not is_ev and validated.get("engine_cc"):
                engine_cc = validated.get("engine_cc")
                engine_wattage = None
                if vehicle_type == "Car":
                    vehicle_category = "Car"
                elif vehicle_type == "Motorcycle":
                    vehicle_category = "Motorcycle"
                else:
                    return JsonResponse({"error": "Unsupported vehicle_type."}, status=400)
                vehicle_tier = VehicleTier.objects.get(vehicle_type=vehicle_category,min_engine_cc__lte=engine_cc,max_engine_cc__gte=engine_cc)
            else:
                return Response(
                    {"engine_cc": ["Please provide engine wattage or engine cc"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            premium_amount = validated.get('premium_amount')

            try:
                plan = InsurancePlan.objects.get(
                    company=company,
                    vehicle_tier=vehicle_tier,
                )
            except InsurancePlan.DoesNotExist:
                print("no plan")
                return Response(
                    {
                        "planErrorDetail": "No matching insurance plan found!",
                        "vehicleTypeError":"Please ensure all the fields are correct.",
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
            if documents and doc_types:
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

            print('test2.1')
            family_member = FamilyMember.objects.get(
                family_member_id=validated.get("family_member_id")
            )
            print('test2.2')
            for reminder in vehicle.reminder_set.all():
                reminder.family_member = family_member
                reminder.save()

            print('test3')
            expiry_date_str = validated.get('insurance_renewal_date')
            bluebook_renewal_date_str = validated.get('bluebook_renewal_date')
            bluebook_renewal_date = datetime.fromisoformat(bluebook_renewal_date_str.replace("Z", "+00:00"))
            expiry_date = datetime.fromisoformat(expiry_date_str.replace("Z", "+00:00"))
            print('test4')

            is_ev = validated.get('is_ev')
            is_ev = is_ev.lower() == "true" if is_ev else False
            vehicle_type = validated.get("vehicle_type")

            print('test5')
            if is_ev and validated.get("engine_wattage"):
                engine_wattage = validated.get("engine_wattage")
                engine_cc = None

                vehicle.engine_wattage = engine_wattage
                if vehicle_type == "Car":
                    vehicle_type = "Car (EV)"
                elif vehicle_type == "Motorcycle":
                    vehicle_type = "Motorcycle (EV)"
                elif vehicle_type == "Car (EV)":
                    pass
                elif vehicle_type == "Motorcycle (EV)":
                    pass
                else:
                    return JsonResponse({"error": "Unsupported vehicle_type."}, status=400)

                vehicle_tier = VehicleTier.objects.get(vehicle_type=vehicle_type,min_engine_wattage__lte=engine_wattage,max_engine_wattage__gte=engine_wattage)
            elif not is_ev and validated.get("engine_cc"):
                engine_cc = validated.get("engine_cc")
                engine_wattage = None
                vehicle.engine_cc = engine_cc
                if vehicle_type == "Car (EV)":
                    vehicle_type = "Car"
                elif vehicle_type == "Motorcycle (EV)":
                    vehicle_type = "Motorcycle"

                elif vehicle_type == "Car":
                    pass
                elif vehicle_type == "Motorcycle":
                    pass
                else:
                    return JsonResponse({"error": "Unsupported vehicle_type."}, status=400)

                print(vehicle_type)
                vehicle_tier = VehicleTier.objects.get(vehicle_type=vehicle_type,min_engine_cc__lte=engine_cc,max_engine_cc__gte=engine_cc)
            else:
                return Response(
                    {"engine_cc": ["Please provide engine wattage or engine cc"]},
                    status=status.HTTP_400_BAD_REQUEST
                )


            vehicle.plate_number = validated.get("plate_number")

            print('test6')

            vehicle.family_member = family_member

            insurance = Insurance.objects.get(vehicle=vehicle)

            print('test7')

            if validated.get("vehicle_image"):
                if vehicle.vehicle_image:
                    try:
                        vehicle.vehicle_image.delete(save=False)
                    except Exception as e:
                        print(f"Error deleting old image from Cloudinary: {e}")


                vehicle.vehicle_image = validated.get("vehicle_image")





            print('test8')
            vehicle.save()

            print('test9')
            # --- Update Insurance fields ---
            if expiry_date is not None:

                insurance.expiry_date = expiry_date

            company = InsuranceCompany.objects.get(id=validated.get("company_id"))
            print('this is ',company)

            plan = InsurancePlan.objects.get( company=company, vehicle_tier=vehicle_tier)
            insurance.plan = plan
            premium_amount = validated.get('premium_amount')
            print(premium_amount)
            insurance.amount = premium_amount
            print(plan)
           # insurance.amount = validated.get("premium_amount")
            insurance.save()
            print('test10')

            bluebook_renewal = BluebookRenewal.objects.get(vehicle=vehicle)
            bluebook_renewal.renewal_date = bluebook_renewal_date
            bluebook_renewal.save()



            documents = request.FILES.getlist('documents')
            doc_types = request.data.getlist('doc_types')
            if documents and doc_types:
                print('test10.1')
                if len(documents) != len(doc_types):
                    return Response(
                        {"detail": "Mismatch between documents and document types count"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                print('test10.2')

                for doc, doc_type in zip(documents, doc_types):
                    print('test10.3')
                    print("DOC TYPE RECEIVED =>", doc_type)

                    VehicleDocument.objects.create(
                        vehicle=vehicle,
                        doc_type=doc_type,
                        image=doc
                    )
                print('test11')
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



@api_view(['POST'])
def predict_vehicle_type(request):
    supported_types = ['Car', 'Motorcycle']
    uploaded_img = request.FILES.get('vehicle_image')
    if not uploaded_img:
        return Response(
            {"vehicleTypeError": "Please upload clear and valid vehicle image or try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    uploaded_img.seek(0)  # Reset file pointer before sending
    predicted_label, confidence = send_image_to_huggingface(uploaded_img)
    if predicted_label and predicted_label in supported_types:
        return Response(
            {
                "predicted_label": predicted_label,

            },
            status=status.HTTP_200_OK,
        )

    else:
        return Response(
            {
                "vehicleTypeError": "Please upload clear and valid vehicle image or try again.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )





