from django.db import models

# Create your models here.

class Family(models.Model):
    family_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.CharField(max_length=200, blank=True, null=True)


    def __str__(self):
        return self.name


    class Meta:       
        verbose_name_plural = "Family"    
    



