from rest_framework import serializers
from .models import VehicleDocument

class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = ["document_id", "vehicle", "doc_type", "uploaded_at", "image"]