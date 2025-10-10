from django.urls import path
from .views import InsuranceCompanyView

urlpatterns =[
path('api/get-companies/',InsuranceCompanyView.as_view(),name = 'get-companies'),


]
