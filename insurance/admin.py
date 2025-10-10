from django.contrib import admin
from .models import Insurance, InsuranceCompany, InsurancePlan


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")   # must be tuple, not string


@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "vehicle_type", "payment_mode", "amount")
    list_filter = ("company", "vehicle_type", "payment_mode")


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = (
        "insurance_id",
        "get_company",
        "get_vehicle_type",
        "get_payment_mode",
        "get_amount",
        "vehicle",
        "insurance_date",
        "expiry_date",
    )
    list_filter = ("plan__company", "plan__vehicle_type", "plan__payment_mode")

    # --- Custom methods to pull data from related InsurancePlan ---
    def get_company(self, obj):
        return obj.plan.company.name
    get_company.short_description = "Company"

    def get_vehicle_type(self, obj):
        return obj.plan.get_vehicle_type_display()
    get_vehicle_type.short_description = "Vehicle Type"

    def get_payment_mode(self, obj):
        return obj.plan.get_payment_mode_display()
    get_payment_mode.short_description = "Payment Mode"

    def get_amount(self, obj):
        return obj.plan.amount
    get_amount.short_description = "Amount"
