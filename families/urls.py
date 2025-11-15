from django.urls import path
from .views import AddFamily
from .views import GetFamilyQR,JoinQR,leave_and_create_family,leave_and_join_family




urlpatterns =[
   path('api/addfamily',AddFamily.as_view(), name='addfamily'),
   path('api/family-qr/',GetFamilyQR.as_view(), name='family-qr'),
   path('api/join-qr/',JoinQR.as_view(), name='join-qr'),
   path('leave-and-create-family/',leave_and_create_family, name='leave-and-create-family'),
   path('leave-and-join-family/',leave_and_join_family, name='leave-and-join-family'),

]


