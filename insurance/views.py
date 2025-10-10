from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import InsuranceCompanySerializer
from .models import InsuranceCompany

class InsuranceCompanyView(APIView):
    def get(self,request):
        companies = InsuranceCompany.objects.all()
        serializer = InsuranceCompanySerializer(companies,many=True)
        print(serializer.data)
        return Response(serializer.data)