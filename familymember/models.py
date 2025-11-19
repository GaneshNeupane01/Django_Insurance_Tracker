from django.db import models
from users.models import UserDetail
from families.models import Family
from django.db import models
from django.contrib.auth.models import User


class FamilyMember(models.Model):
    family_member_id = models.AutoField(primary_key=True)
    family = models.ForeignKey(Family,on_delete=models.CASCADE)
    user = models.ForeignKey(UserDetail,on_delete=models.CASCADE,unique=True) #or onetoone field
    #user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=100)

    class Meta:       
        verbose_name_plural = "FamilyMember"

    def __str__(self):
        #return first_name plus last name
        return self.user.user.first_name + ' ' + self.user.user.last_name