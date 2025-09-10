from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserDetail(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    class Meta:       
        verbose_name_plural = "UserDetail"  



