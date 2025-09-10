from django.contrib import admin
from vehicledocument.models import VehicleDocument



@admin.register(VehicleDocument)
class VehicleDocumentsAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'vehicle','file_path','doc_type') 

