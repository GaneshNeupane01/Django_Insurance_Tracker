
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




class AddVehicleSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(required=False)
    family_member_id = serializers.IntegerField()
   # name = serializers.CharField(max_length=20)
    company_id = serializers.IntegerField()
    plate_number = serializers.CharField(max_length=30)
    engine_cc = serializers.IntegerField()
   # insurance_company = serializers.CharField(max_length=30)
    insurance_renewal_date = serializers.CharField()
    payment_mode = serializers.CharField(max_length=20)
    premium_amount = serializers.DecimalField(max_digits=10, decimal_places=2,required=False)
   # vehicle_document_type = serializers.CharField(max_length=20,required=False)
   # image = serializers.ImageField(required=False)
    vehicle_image = serializers.ImageField(required=True)

    def validate_engine_cc(self, value):
        if value <= 0:
            raise serializers.ValidationError("Engine CC must be positive.")
        return value

    def validate_premium_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Premium must be greater than 0.")
        return value

    def validate_insurance_renewal_date(self, value):
        from django.utils import timezone
        from datetime import datetime
        try:
            expiry_date = datetime.strptime(value, "%m/%d/%Y")
        except ValueError:
            raise serializers.ValidationError("Date must be MM/DD/YYYY.")
        if expiry_date.date() < timezone.now().date():
            raise serializers.ValidationError("Expiry date cannot be in the past.")
        return value

    def validate_family_member_id(self, value):
        from familymember.models import FamilyMember
        if not FamilyMember.objects.filter(family_member_id=value).exists():
            raise serializers.ValidationError("Invalid family member ID.")
        return value
