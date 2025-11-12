from django.contrib import admin
from .models import Insurance, InsuranceCompany, InsurancePlan,VehicleTier


@admin.register(VehicleTier)
class VehicleTierAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle_type", "min_engine_cc", "max_engine_cc", "min_engine_wattage", "max_engine_wattage")

@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")   # must be tuple, not string


@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "vehicle_tier","amount")
    list_filter = ("company", "vehicle_tier")


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = (
        "insurance_id",
        "get_company",
        "get_vehicle_tier",

        "get_amount",
        "vehicle",
        "insurance_date",
        "expiry_date",
    )
    list_filter = ("plan__company", "plan__vehicle_tier")

    # --- Custom methods to pull data from related InsurancePlan ---
    def get_company(self, obj):
        return obj.plan.company.name
    get_company.short_description = "Company"

    def get_vehicle_tier(self, obj):
        return obj.plan.vehicle_tier
    get_vehicle_tier.short_description = "Vehicle Type"


    def get_amount(self, obj):
        return obj.plan.amount
    get_amount.short_description = "Amount"
