from rest_framework import serializers
from rest_framework import serializers

from users.serializers import UserDetailSerializer
from families.serializers import FamilySerializer
from familymember.models import FamilyMember
from vehicles.models import Vehicle

class FamilyMemberSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    family = FamilySerializer()
    vehicle_count = serializers.SerializerMethodField()


    class Meta:
        model = FamilyMember
        fields = ["family_member_id", "role", "user", "family", "vehicle_count"]

    def get_vehicle_count(self, obj):
        return Vehicle.objects.filter(family_member=obj).count()