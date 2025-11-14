
from rest_framework import serializers
from .models import Vehicle,BluebookRenewal
from vehicledocument.serializers import VehicleDocumentSerializer


from insurance.serializers import InsuranceSerializer
from DjangoModels.utils.date_converter import ad_to_bs


from rest_framework import serializers




from users.serializers import UserDetailSerializer
from families.serializers import FamilySerializer
from familymember.models import FamilyMember
from datetime import datetime, timezone


class FamilyMemberSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    family = FamilySerializer()


    class Meta:
        model = FamilyMember
        fields = ["family_member_id", "role", "user", "family"]



class BluebookRenewalSerializer(serializers.ModelSerializer):
    renewal_date_bs = serializers.SerializerMethodField()

    class Meta:
        model = BluebookRenewal
        fields = ["renewal_date_bs","renewal_date"]
    def get_renewal_date_bs(self, obj):
        return ad_to_bs(obj.renewal_date)


class VehicleSerializer(serializers.ModelSerializer):

    family_member = FamilyMemberSerializer(read_only=True)
    documents = VehicleDocumentSerializer(source="vehicledocument_set", many=True, read_only=True)
   # reminders = ReminderSerializer(source="reminder_set", many=True, read_only=True)
    insurances = InsuranceSerializer(source="insurance_set.first",read_only=True)
    bluebook_renewals = BluebookRenewalSerializer(source="bluebook_renewals.first",read_only=True)


    class Meta:
        model = Vehicle
        fields = "__all__"


class AddVehicleSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(required=False)
    family_member_id = serializers.IntegerField()
   # name = serializers.CharField(max_length=20)
    company_id = serializers.IntegerField()
    plate_number = serializers.CharField(max_length=30)
    engine_cc = serializers.IntegerField(required=False)
    engine_wattage = serializers.IntegerField(required=False)
    vehicle_category = serializers.CharField(max_length=40)
   # insurance_company = serializers.CharField(max_length=30)
    insurance_renewal_date = serializers.CharField()
    bluebook_renewal_date = serializers.CharField(required=False)
   # insurance_renewal_date_bs = serializers.CharField(required=False)
    payment_mode = serializers.CharField(max_length=20,required=False)
    premium_amount = serializers.DecimalField(max_digits=10, decimal_places=2,required=False)
   # vehicle_document_type = serializers.CharField(max_length=20,required=False)
   # image = serializers.ImageField(required=False)
    vehicle_image = serializers.ImageField(required=True)

    def validate_engine_cc(self, value):
        if value <= 0:
            raise serializers.ValidationError("Engine CC must be positive.")
        return value

    def validate_engine_wattage(self, value):
        if value <= 0:
            raise serializers.ValidationError("Engine wattage must be positive.")
        return value

    def validate_premium_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Premium must be greater than 0.")
        return value

    def validate_insurance_renewal_date(self, value):
        # Parse the ISO string into a datetime object
        expiry_date = datetime.fromisoformat(value.replace("Z", "+00:00"))

        # Validate that it’s not in the past
        if expiry_date.date() < datetime.now(timezone.utc).date():
            raise serializers.ValidationError("Expiry date cannot be in the past.")
        return value

    def validate_family_member_id(self, value):
        from familymember.models import FamilyMember
        if not FamilyMember.objects.filter(family_member_id=value).exists():
            raise serializers.ValidationError("Invalid family member ID.")
        return value




class EditVehicleSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(required=False)
    family_member_id = serializers.IntegerField()
   # name = serializers.CharField(max_length=20)
    company_id = serializers.IntegerField()
    plate_number = serializers.CharField(max_length=30)
    engine_cc = serializers.IntegerField(required=False)
    engine_wattage = serializers.IntegerField(required=False)
    vehicle_category = serializers.CharField(max_length=40)
   # insurance_company = serializers.CharField(max_length=30)
    insurance_renewal_date = serializers.CharField(required=False)
    payment_mode = serializers.CharField(max_length=20)
    premium_amount = serializers.DecimalField(max_digits=10, decimal_places=2,required=False)
   # vehicle_document_type = serializers.CharField(max_length=20,required=False)
   # image = serializers.ImageField(required=False)
    vehicle_image = serializers.ImageField(required=False)

    def validate_engine_cc(self, value):
        if value <= 0:
            raise serializers.ValidationError("Engine CC must be positive.")
        return value

    def validate_engine_wattage(self, value):
        if value <= 0:
            raise serializers.ValidationError("Engine wattage must be positive.")
        return value

    def validate_premium_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Premium must be greater than 0.")
        return value

    def validate_insurance_renewal_date(self, value):
        # Parse the ISO string into a datetime object
        expiry_date = datetime.fromisoformat(value.replace("Z", "+00:00"))

        # Validate that it’s not in the past
        if expiry_date.date() < datetime.now(timezone.utc).date():
            raise serializers.ValidationError("Expiry date cannot be in the past.")
        return value


    def validate_family_member_id(self, value):
        from familymember.models import FamilyMember
        if not FamilyMember.objects.filter(family_member_id=value).exists():
            raise serializers.ValidationError("Invalid family member ID.")
        return value
