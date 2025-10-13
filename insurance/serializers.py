
from rest_framework import serializers
from .models import Insurance,InsuranceCompany,InsurancePlan


class InsuranceCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCompany
        fields = "__all__"


class InsurancePlanSerializer(serializers.ModelSerializer):
    company = InsuranceCompanySerializer()

    class Meta:
        model = InsurancePlan
        fields = "__all__"


class InsuranceSerializer(serializers.ModelSerializer):
    plan = InsurancePlanSerializer()
    insurance_date = serializers.DateTimeField(format="%m/%d/%Y", read_only=True)
    expiry_date = serializers.DateTimeField(
        format="%b %d, %Y",
        read_only=True
    )


    class Meta:
        model = Insurance
        fields = "__all__"