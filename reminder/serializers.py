from rest_framework import serializers
from insurance.serializers import InsuranceSerializer
from vehicles.serializers import BluebookRenewalSerializer
from DjangoModels.utils.date_converter import ad_to_bs


from rest_framework import serializers
from .models import Reminder



class ReminderSerializer(serializers.ModelSerializer):
   # insurance = InsuranceSerializer(source="vehicle.insurance_set.first",read_only=True)
   # bluebook = BluebookRenewalSerializer(source="vehicle.bluebook_renewals.first", read_only=True)
    vehicle = serializers.StringRelatedField()
    family_member = serializers.StringRelatedField()
    is_expired = serializers.SerializerMethodField()
    snoozed_until = serializers.DateTimeField(format=None, read_only=True)
    snoozed_until_bs = serializers.SerializerMethodField()
    renewal_date_bs = serializers.SerializerMethodField()
    target_type_id = serializers.SerializerMethodField()
    frequency = serializers.SerializerMethodField()
   # vehicle_image = serializers.ImageField(source="vehicle.vehicle_image", read_only=True)
    


    class Meta:
        model = Reminder
        fields = ["reminder_id", "target_type","target_type_id", "snoozed_until","snoozed_until_bs", "is_active", "vehicle", "family_member", "is_expired",'frequency','renewal_date_bs']

    def get_is_expired(self, obj):
        return obj.is_expired
    def get_snoozed_until_bs(self, obj):
        return ad_to_bs(obj.snoozed_until)
    def get_renewal_date_bs(self, obj):
        if obj.target_type == "insurance" and obj.vehicle.insurance_set.exists():
            ins = obj.vehicle.insurance_set.first()
            return ad_to_bs(ins.expiry_date) if ins.expiry_date else None
        elif obj.target_type == "bluebook" and obj.vehicle.bluebook_renewals.exists():
            bb = obj.vehicle.bluebook_renewals.first()
            return ad_to_bs(bb.renewal_date) if bb.renewal_date else None
        return None

    def get_frequency(self,obj):
        return obj.get_frequency_display()
    def get_target_type_id(self,obj):
        if obj.target_type == "insurance" and obj.vehicle.insurance_set.exists():
            ins = obj.vehicle.insurance_set.first()
            return ins.insurance_id
        elif obj.target_type == "bluebook" and obj.vehicle.bluebook_renewals.exists():
            bb = obj.vehicle.bluebook_renewals.first()
            return bb.id
        return None