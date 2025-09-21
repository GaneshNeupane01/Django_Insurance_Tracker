from django.urls import path
from .views import AddFamily
from .views import GetFamilyQR,JoinQR


urlpatterns =[
   path('api/addfamily',AddFamily.as_view(), name='addfamily'),
   path('api/family-qr/',GetFamilyQR.as_view(), name='family-qr'),
   path('api/join-qr/',JoinQR.as_view(), name='join-qr'),
]


