from rest_framework import serializers
from insurance.serializers import InsuranceSerializer
from DjangoModels.utils.date_converter import ad_to_bs


from rest_framework import serializers
from .models import Reminder



class ReminderSerializer(serializers.ModelSerializer):
    insurance = InsuranceSerializer(read_only=True)
    vehicle = serializers.StringRelatedField()
    family_member = serializers.StringRelatedField()
    is_expired = serializers.SerializerMethodField()
    snoozed_until = serializers.DateTimeField(format=None, read_only=True)
    snoozed_until_bs = serializers.SerializerMethodField()
    class Meta:
        model = Reminder
        fields = ["reminder_id", "target_type", "snoozed_until","snoozed_until_bs", "is_active", "vehicle", "family_member", "insurance", "is_expired",'frequency']

    def get_is_expired(self, obj):
        return obj.is_expired
    def get_snoozed_until_bs(self, obj):
        return ad_to_bs(obj.snoozed_until)