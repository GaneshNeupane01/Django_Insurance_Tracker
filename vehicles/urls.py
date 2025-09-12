from django.urls import path
from .views import VehicleListView

urlpatterns = [
   path('api/get-vehicles/',VehicleListView.as_view(),name='get_vehicles'),
    path('api/set-vehicles/',VehicleListView.as_view(),name='set_vehicles'),

]