from django.contrib import admin
from .models import Vehicle,BluebookRenewal

@admin.register(Vehicle)
class VehiclesAdmin(admin.ModelAdmin):
    list_display = ('vehicle_id', 'get_username','plate_number','get_engine_capacity','vehicle_type')

    def get_username(self, obj):
        return obj.family_member.user.user.first_name + ' ' + obj.family_member.user.user.last_name + ' (' + obj.family_member.family.name + ')'
    get_username.short_description = 'Family Member'

    def get_engine_capacity(self, obj):
        if obj.engine_cc:
            return f"{obj.engine_cc} CC"
        elif obj.engine_wattage:
            return f"{obj.engine_wattage} Watts"
        else:
            return "N/A"
    get_engine_capacity.short_description = 'Engine Capacity'



@admin.register(BluebookRenewal)
class BluebookRenewalAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'renewal_date')




