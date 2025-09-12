from django.db import models
from reminder.models import Reminder
from vehicles.models import Vehicle


# Create your models here.


class Insurance(models.Model):
    insurance_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True,blank=True)
    insurance_company = models.CharField(max_length=50)
    payment_mode = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    insurance_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(auto_now_add=False)

    class Meta:       
        verbose_name_plural = "Insurance"  

