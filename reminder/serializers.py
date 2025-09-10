from rest_framework import serializers
from insurance.serializers import InsuranceSerializer


from rest_framework import serializers
from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    insurance_set = InsuranceSerializer(many=True, read_only=True)
    vehicle = serializers.StringRelatedField()  # or 'vehicles.VehicleSerializer' as string
    family_member = serializers.StringRelatedField()  # optional

    class Meta:
        model = Reminder
        fields = ["reminder_id", "target_type", "reminder_date", "snoozed_until", "is_active", "insurance_set", "vehicle", "family_member"]
