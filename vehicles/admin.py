from django.contrib import admin
from .models import Vehicle,BluebookRenewal

@admin.register(Vehicle)
class VehiclesAdmin(admin.ModelAdmin):
    list_display = ('vehicle_id', 'get_username','plate_number','engine_cc','name')

    def get_username(self, obj):
        return obj.family_member.user.user.username



@admin.register(BluebookRenewal)
class BluebookRenewalAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'renewal_date')




