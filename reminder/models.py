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
            ('1d', '1 day before expiry'),
            ('3d', '3 days before expiry'),
            ('7d', '1 week before expiry'),
            ('14d', '2 weeks before expiry'),
            ('30d', '30 days before expiry'),
        ]

    reminder_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    #insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, null=True, blank=True)
    family_member = models.ForeignKey(FamilyMember,on_delete=models.CASCADE)
    target_type = models.CharField(max_length=30,default="insurance")
    last_sent = models.DateTimeField(null=True, blank=True)
    snoozed_until = models.DateTimeField(auto_now_add=False,null=True,blank=True)
    is_active = models.BooleanField(default=False)
    #is_expired = models.BooleanField(default=False)
    #choices field for frequency of reminder_date like weekly,daily,monthly
    frequency = models.CharField(max_length=30,default="1d",choices=FrequencyChoices)
    frequency_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:       
        verbose_name_plural = "Reminder"

    def __str__(self):
        return f"Reminder for {self.vehicle.plate_number} by {self.family_member.user.user.username}"


    @property
    def is_expired(self):
        #expiry_date based on target_type
        if self.target_type == 'insurance':
            insurance = self.vehicle.insurance_set.order_by('-expiry_date').first()
            expiry_date = insurance.expiry_date if insurance else None

        elif self.target_type == 'bluebook':
            bluebook = self.vehicle.bluebook_renewals.order_by('-renewal_date').first()
            expiry_date = bluebook.renewal_date if bluebook else None

        if expiry_date:
            return timezone.now() >= expiry_date
        return False



    def should_notify(self):


        if self.target_type == 'insurance':
            insurance = self.vehicle.insurance_set.order_by('-expiry_date').first()
            expiry_date = insurance.expiry_date if insurance else None
        elif self.target_type == 'bluebook':
            bluebook = self.vehicle.bluebook_renewals.order_by('-renewal_date').first()
            expiry_date = bluebook.renewal_date if bluebook else None
        else:
            return False

        now = timezone.now()


        if self.snoozed_until:
            if self.snoozed_until <= now:

                self.snoozed_until = None
                self.is_active = True
                self.save()
                return True
            return False  # still snoozed


        frequency_map = {
            "1d": timedelta(days=1),
            "3d": timedelta(days=3),
            "7d": timedelta(days=7),
            "14d": timedelta(days=14),
            "30d": timedelta(days=30),

        }
        reminder_window = frequency_map.get(self.frequency, timedelta(days=1))


        if not expiry_date:
            return False

        try:
            # if expiry_date is a date object (not datetime)
            days_left = (expiry_date - now.date()).days
        except Exception:
            # expiry_date is datetime
            days_left = (expiry_date - now).days

        # Only proceed if we're within the chosen window
        if days_left <= reminder_window.days:

            if self.last_sent is None:
                return True

            if self.frequency_updated_at and self.frequency_updated_at > self.last_sent:
                return True

            if (now - self.last_sent) >= reminder_window:
                return True

        return False
