from django.urls import path
from .views import RemindersView,ReminderTrigger,SavenReminderConfig,save_token,test_notification,mark_renewed,run_notifications_job

urlpatterns = [
   path('api/get-reminders/',RemindersView.as_view(),name='get-reminders'),
   path('api/trigger-reminder/',ReminderTrigger,name='snooze-reminder'),
   path('api/save-reminder-config/',SavenReminderConfig,name='save-reminder-config'),
   path('api/save-token/', save_token, name='save_token'),
   path('api/test-notification/', test_notification, name='test_notification'),
   path('api/mark-renewed/', mark_renewed, name='mark_renewed'),
   path('api/run-notifications-job/', run_notifications_job, name='run_notifications_job'),


]