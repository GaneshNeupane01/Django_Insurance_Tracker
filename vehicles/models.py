from django.db import models
from familymember.models import FamilyMember
from cloudinary_storage.storage import MediaCloudinaryStorage


# Create your models here.

class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    family_member = models.ForeignKey(FamilyMember,on_delete=models.CASCADE,blank=True,null=True)
    plate_number = models.CharField(max_length=20)
    engine_cc = models.IntegerField(blank=True,null=True)
    engine_wattage = models.IntegerField(blank=True,null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    vehicle_image = models.ImageField(upload_to='vehicle_images/',blank=True,null=True,storage=MediaCloudinaryStorage())


    def __str__(self):
        return f"{self.plate_number} - {self.vehicle_type or 'N/A'}"

    class Meta:       
        verbose_name_plural = "Vehicle"  


class BluebookRenewal(models.Model):
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name='bluebook_renewals')
    renewal_date = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return f"{self.renewal_date} for {self.vehicle}"


    class Meta:
        verbose_name_plural = "BluebookRenewal"