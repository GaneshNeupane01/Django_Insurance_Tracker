from django.contrib import admin
from reminder.models import Reminder,ExpoPushToken
# Register your models here.

@admin.register(Reminder)
class RemindersAdmin(admin.ModelAdmin):
    list_display = ('reminder_id', 'vehicle','family_member','target_type','is_active') 

@admin.register(ExpoPushToken)
class ExpoPushTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'updated_at')