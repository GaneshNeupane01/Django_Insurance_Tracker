
from rest_framework import serializers
from .models import Vehicle
from vehicledocument.serializers import VehicleDocumentSerializer





from insurance.serializers import InsuranceSerializer


from rest_framework import serializers
from reminder.models import Reminder




from users.serializers import UserDetailSerializer
from families.serializers import FamilySerializer
from familymember.models import FamilyMember

class FamilyMemberSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    family = FamilySerializer()


    class Meta:
        model = FamilyMember
        fields = ["family_member_id", "role", "user", "family"]



class ReminderSerializer(serializers.ModelSerializer):
    insurance_set = InsuranceSerializer(many=True, read_only=True)
    vehicle = serializers.StringRelatedField()
    family_member = serializers.StringRelatedField()
    class Meta:
        model = Reminder
        fields = ["reminder_id", "target_type", "reminder_date", "snoozed_until", "is_active", "insurance_set", "vehicle", "family_member"]


class VehicleSerializer(serializers.ModelSerializer):
    #family_member = serializers.FamilyMemberSerializer()
    #vehicledocument_set = VehicleDocumentSerializer(many=True, read_only=True)  # reverse FK
    #reminder_set = serializers.ReminderSerializer(many=True, read_only=True)
    family_member = FamilyMemberSerializer(read_only=True)
    documents = VehicleDocumentSerializer(source="vehicledocument_set", many=True, read_only=True)
    reminders = ReminderSerializer(source="reminder_set", many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = "__all__"

