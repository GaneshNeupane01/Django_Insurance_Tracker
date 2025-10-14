from django.urls import path
from .views import RemindersView,ReminderTrigger,SavenReminderConfig,save_token

urlpatterns = [
   path('api/get-reminders/',RemindersView.as_view(),name='get-reminders'),
   path('api/trigger-reminder/',ReminderTrigger,name='snooze-reminder'),
   path('api/save-reminder-config/',SavenReminderConfig,name='save-reminder-config'),
   path('api/save-token/', save_token, name='save_token'),



]