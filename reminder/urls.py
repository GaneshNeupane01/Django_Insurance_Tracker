from django.urls import path
from .views import RemindersView

urlpatterns = [
   path('api/get-reminders/',RemindersView.as_view(),name='get-reminders'),

]