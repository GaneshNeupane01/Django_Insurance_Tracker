from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
# Create your models here.

class UserDetail(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profile = models.ImageField(upload_to='profile_pics/',blank=True,null=True,storage=MediaCloudinaryStorage())
    profile_url = models.URLField(blank=True,null=True)
    phone_number = models.CharField(max_length=10,blank=True,null=True)


    def __str__(self):
        return self.user.username
    class Meta:       
        verbose_name_plural = "UserDetail"  



