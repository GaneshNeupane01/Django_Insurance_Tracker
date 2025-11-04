from django.db import models
from familymember.models import FamilyMember
from cloudinary_storage.storage import MediaCloudinaryStorage


# Create your models here.

class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    family_member = models.ForeignKey(FamilyMember,on_delete=models.CASCADE,blank=True,null=True)
    plate_number = models.CharField(max_length=20)
    engine_cc = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    vehicle_image = models.ImageField(upload_to='vehicle_images/',blank=True,null=True,storage=MediaCloudinaryStorage())


    def __str__(self):
        return self.plate_number

    class Meta:       
        verbose_name_plural = "Vehicle"  


