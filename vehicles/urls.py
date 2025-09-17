from django.urls import path
from .views import VehicleListView,EditVehicleView


urlpatterns = [
   path('api/get-vehicles/',VehicleListView.as_view(),name='get_vehicles'),
    path('api/set-vehicles/',VehicleListView.as_view(),name='set_vehicles'),
    path('api/edit-vehicle/',EditVehicleView.as_view(),name='edit_vehicle'),
    #path('api/vehicle/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),')

]