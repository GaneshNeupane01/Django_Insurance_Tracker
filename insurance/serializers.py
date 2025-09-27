
from rest_framework import serializers
from .models import Insurance

class InsuranceSerializer(serializers.ModelSerializer):
    expiry_date = serializers.DateTimeField(format="%m/%d/%Y", read_only=True)

    class Meta:
        model = Insurance
        fields = "__all__"