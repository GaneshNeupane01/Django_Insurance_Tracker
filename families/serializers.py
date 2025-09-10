from rest_framework import serializers
from .models import Family
class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ["family_id", "name", "created_at"]