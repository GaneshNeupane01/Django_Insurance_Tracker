
from rest_framework import serializers
from .models import Vehicle
from vehicledocument.serializers import VehicleDocumentSerializer


from insurance.serializers import InsuranceSerializer


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





class VehicleSerializer(serializers.ModelSerializer):

    family_member = FamilyMemberSerializer(read_only=True)
    documents = VehicleDocumentSerializer(source="vehicledocument_set", many=True, read_only=True)
   # reminders = ReminderSerializer(source="reminder_set", many=True, read_only=True)
    insurances = InsuranceSerializer(source="insurance_set.first",read_only=True)
   

    class Meta:
        model = Vehicle
        fields = "__all__"

