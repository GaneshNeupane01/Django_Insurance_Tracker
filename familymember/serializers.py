from rest_framework import serializers
from rest_framework import serializers

from users.serializers import UserDetailSerializer
from families.serializers import FamilySerializer
from familymember.models import FamilyMember

class FamilyMemberSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    family = FamilySerializer()


    class Meta:
        model = FamilyMember
        fields = ["family_member_id", "role", "user", "family"]