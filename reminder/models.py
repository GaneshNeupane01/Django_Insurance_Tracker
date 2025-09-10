from django.db import models
from vehicles.models import Vehicle
from familymember.models import FamilyMember



class Reminder(models.Model):
    reminder_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    family_member = models.ForeignKey(FamilyMember,on_delete=models.CASCADE)
    target_type = models.CharField(max_length=30)
    reminder_date = models.DateTimeField(auto_now_add=True)
    snoozed_until = models.DateTimeField(auto_now_add=False)
    is_active = models.BooleanField(default=False)

    class Meta:       
        verbose_name_plural = "Reminder"

    def __str__(self):
        return f"Reminder for {self.vehicle.plate_number} by {self.family_member.user.user.username}"


