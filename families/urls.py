from django.urls import path
from .views import AddFamily


urlpatterns =[
   path('api/addfamily',AddFamily.as_view(), name='addfamily'),


]