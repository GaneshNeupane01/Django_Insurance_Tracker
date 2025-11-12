from django.urls import path
from .views import InsuranceCompanyView,get_premium_amount

urlpatterns =[
path('api/get-companies/',InsuranceCompanyView.as_view(),name = 'get-companies'),
 path('api/get-premium-amount/', get_premium_amount, name='get_premium_amount'),


]
