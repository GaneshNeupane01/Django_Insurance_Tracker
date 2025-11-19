from django.db import models

from vehicles.models import Vehicle



# Create your models here.

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    class Meta:
         verbose_name_plural = "InsuranceCompany"



class VehicleTier(models.Model):

    VEHICLE_CHOICES = [
        ("Car (EV)", "Car (EV)"),
        ("Car", "Car"),
        ("Motorcycle (EV)", "Motorcycle (EV)"),
        ("Motorcycle", "Motorcycle"),
    ]

    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_CHOICES)

    min_engine_cc = models.IntegerField(null=True, blank=True, help_text="Minimum CC (non-EVs)")
    max_engine_cc = models.IntegerField(null=True, blank=True, help_text="Maximum CC (non-EVs)")

    min_engine_wattage = models.IntegerField(null=True, blank=True, help_text="Minimum Wattage (EVs)")
    max_engine_wattage = models.IntegerField(null=True, blank=True, help_text="Maximum Wattage (EVs)")

    class Meta:
        verbose_name = "Vehicle Tier"
        verbose_name_plural = "Vehicle Tiers"
        unique_together = ('vehicle_type', 'min_engine_cc', 'max_engine_cc', 'min_engine_wattage', 'max_engine_wattage')

    def __str__(self):
        if 'EV' in self.vehicle_type:
            return f"{self.get_vehicle_type_display()} ({self.min_engine_wattage}W - {self.max_engine_wattage}W)"
        return f"{self.get_vehicle_type_display()} ({self.min_engine_cc}CC - {self.max_engine_cc}CC)"




class InsurancePlan(models.Model):

    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name="plans")

    vehicle_tier = models.ForeignKey(VehicleTier, on_delete=models.CASCADE, related_name="plans")

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("company", "vehicle_tier")
        verbose_name_plural = "InsurancePlan"

    def __str__(self):
        return f"{self.company.name} - {self.vehicle_tier}"



class Insurance(models.Model):
    insurance_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True,blank=True,related_name="insurance_set")
    plan = models.ForeignKey(InsurancePlan, on_delete=models.CASCADE, related_name="insurances",null=True,blank=True)
    #insurance_company = models.CharField(max_length=50)
    #payment_mode = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    insurance_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(auto_now_add=False)

    class Meta:       
        verbose_name_plural = "Insurance"

    def __str__(self):
        return f"Insurance for {self.plan.vehicle_tier} ({self.plan.company.name})"


