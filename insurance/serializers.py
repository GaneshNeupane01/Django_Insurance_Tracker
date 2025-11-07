
from rest_framework import serializers
from .models import Insurance,InsuranceCompany,InsurancePlan

from DjangoModels.utils.date_converter import ad_to_bs


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
    expiry_date_bs = serializers.SerializerMethodField()




    class Meta:
        model = Insurance
        fields = "__all__"

    def get_expiry_date_bs(self, obj):
        return ad_to_bs(obj.expiry_date)