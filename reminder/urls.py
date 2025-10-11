from django.urls import path
from .views import RemindersView,ReminderTrigger

urlpatterns = [
   path('api/get-reminders/',RemindersView.as_view(),name='get-reminders'),
   path('api/trigger-reminder/',ReminderTrigger,name='snooze-reminder'),

]