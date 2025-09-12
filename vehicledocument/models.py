from django.db import models
from vehicles.models import Vehicle
# Create your models here.


class VehicleDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle,on_delete= models.CASCADE)
   # file_path = models.CharField(max_length=30)
    doc_type = models.CharField(max_length=30)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images',blank=True,null=True)

    def __str__(self):
        return self.doc_type

    class Meta:       
        verbose_name_plural = "VehicleDocument"  