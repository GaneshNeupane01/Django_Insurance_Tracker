from django.db import models
from vehicles.models import Vehicle
from familymember.models import FamilyMember
from insurance.models import Insurance
from django.utils import timezone
from datetime import datetime, timedelta
from users.models import UserDetail



class ExpoPushToken(models.Model):
    user = models.OneToOneField(UserDetail, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)


class Reminder(models.Model):

    FrequencyChoices = [
            ('1d', 'Daily'),
            ('3d', '3 Days'),
            ('7d', 'Weekly'),
            ('14d', '14 Days'),
            ('30d', 'Monthly'),
        ]

    reminder_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, null=True, blank=True)
    family_member = models.ForeignKey(FamilyMember,on_delete=models.CASCADE)
    target_type = models.CharField(max_length=30,default="insurance")
    last_sent = models.DateTimeField(null=True, blank=True)
    snoozed_until = models.DateTimeField(auto_now_add=False,null=True,blank=True)
    is_active = models.BooleanField(default=False)
    #is_expired = models.BooleanField(default=False)
    #choices field for frequency of reminder_date like weekly,daily,monthly
    frequency = models.CharField(max_length=30,default="7d",choices=FrequencyChoices)

    class Meta:       
        verbose_name_plural = "Reminder"

    def __str__(self):
        return f"Reminder for {self.vehicle.plate_number} by {self.family_member.user.user.username}"


    @property
    def is_expired(self):
        if self.insurance and self.insurance.expiry_date:
            return timezone.now() >= self.insurance.expiry_date
        return False

    def should_notify(self):
        now = datetime.now()
        if self.snoozed_until and self.snoozed_until < now:
            self.snoozed_until = None
            self.is_active = True
            self.save()
            return True

        if self.snoozed_until and self.snoozed_until > now:
            return False  # user snoozed

        if self.last_sent is None:
            return True

        if self.frequency == 'daily' and (now - self.last_sent) >= timedelta(days=1):
            return True
        if self.frequency == 'weekly' and (now - self.last_sent) >= timedelta(weeks=1):
            return True
        if self.frequency == 'monthly' and (now - self.last_sent) >= timedelta(days=30):
            return True

        return False