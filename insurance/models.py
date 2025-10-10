from django.db import models

from vehicles.models import Vehicle


# Create your models here.

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    class Meta:
         verbose_name_plural = "InsuranceCompany"


class InsurancePlan(models.Model):
    VEHICLE_TYPES = [
        ("Car", "Car"),
        ("Motorcycle", "Bike"),
        ("Truck", "Truck"),
        ("Bus", "Bus"),
    ]

    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name="plans")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES,default='Motorcycle')
    payment_mode = models.CharField(max_length=30, choices=[("monthly", "Monthly"), ("yearly", "Yearly")])
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("company", "vehicle_type", "payment_mode")
        verbose_name_plural = "InsurancePlan"

    def __str__(self):
        return f"{self.company.name} - {self.get_vehicle_type_display()} ({self.amount})"






class Insurance(models.Model):
    insurance_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True,blank=True)
    plan = models.ForeignKey(InsurancePlan, on_delete=models.CASCADE, related_name="insurances",null=True,blank=True)
    #insurance_company = models.CharField(max_length=50)
    #payment_mode = models.CharField(max_length=30)
    #amount = models.DecimalField(max_digits=10,decimal_places=2)
    insurance_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(auto_now_add=False)

    class Meta:       
        verbose_name_plural = "Insurance"

    def __str__(self):
        return f"Insurance for {self.plan.get_vehicle_type_display()} ({self.plan.company.name})"


