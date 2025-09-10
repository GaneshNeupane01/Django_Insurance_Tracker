from django.contrib import admin
from .models import FamilyMember

# Register your models here.

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('family_member_id','family','role','user','vehicle_count')

    def vehicle_count(self, obj):
        return obj.vehicle_set.count() 
    vehicle_count.short_description = 'Vehicles'