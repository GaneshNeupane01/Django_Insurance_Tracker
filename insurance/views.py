from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import InsuranceCompanySerializer
from .models import InsuranceCompany,InsurancePlan,VehicleTier
from rest_framework.decorators import api_view
from django.http import JsonResponse

class InsuranceCompanyView(APIView):
    def get(self,request):
        companies = InsuranceCompany.objects.all()
        serializer = InsuranceCompanySerializer(companies,many=True)
        print(serializer.data)
        return Response(serializer.data)


@api_view(['GET'])
def get_premium_amount(request):
    company_id = request.GET.get("company_id")
    vehicle_type = request.GET.get("vehicle_type")

    isEV = request.GET.get("is_ev")
    isEV = isEV.lower() == "true" if isEV else False
    engine_cc = request.GET.get("engine_cc")
    engine_wattage = request.GET.get("engine_wattage")
    try:
        company = InsuranceCompany.objects.get(pk=company_id)
    except InsuranceCompany.DoesNotExist:
        return JsonResponse({"error": "Invalid company_id."}, status=404)
    #premium amount calculation
    try:
        if isEV and engine_wattage:
            if vehicle_type == "Car" or vehicle_type == "Car (EV)":
                category = "Car (EV)"
            elif vehicle_type == "Motorcycle" or vehicle_type == "Motorcycle (EV)":
                category = "Motorcycle (EV)"
            else:
                return JsonResponse({"error": "Unsupported vehicle_type."}, status=400)
            vehicle_tier = VehicleTier.objects.get(vehicle_type=category, min_engine_wattage__lte=engine_wattage, max_engine_wattage__gte=engine_wattage)
            plan = InsurancePlan.objects.get(company=company, vehicle_tier=vehicle_tier)
            premium_amount = plan.amount
        elif not isEV and engine_cc:
            if vehicle_type == "Car" or vehicle_type == "Car (EV)":
                category = "Car"
            elif vehicle_type == "Motorcycle" or vehicle_type == "Motorcycle (EV)":
                category = "Motorcycle"
            else:
                return JsonResponse({"error": "Unsupported vehicle_type."}, status=400)
            vehicle_tier = VehicleTier.objects.get(vehicle_type=category,min_engine_cc__lte=engine_cc,max_engine_cc__gte=engine_cc)
            plan = InsurancePlan.objects.get(company=company, vehicle_tier=vehicle_tier)
            premium_amount = plan.amount
        else:
            return JsonResponse({"error": "Invalid engine parameters."}, status=400)
        return JsonResponse({"premium_amount": premium_amount}, status=200)
    except InsurancePlan.DoesNotExist:
        return JsonResponse({"error": "Internal error.No InsurancePlan!"}, status=500)