from django.urls import path
from .views import VehicleListView,EditVehicleView,delete_vehicle,predict_vehicle_type




urlpatterns = [
   path('api/get-vehicles/',VehicleListView.as_view(),name='get_vehicles'),
    path('api/set-vehicles/',VehicleListView.as_view(),name='set_vehicles'),
    path('api/edit-vehicle/',EditVehicleView.as_view(),name='edit_vehicle'),
    path('delete-vehicle/<int:pk>/', delete_vehicle, name='delete_vehicle'),
    path('predict-vehicle-type/', predict_vehicle_type, name='predict_vehicle_type'),




    #path('api/vehicle/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),')

]