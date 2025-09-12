from django.urls import path
from .views import FamilyMemberView

urlpatterns = [
path('api/get-members/', FamilyMemberView.as_view(), name='get-members'),
path('api/add-member/', FamilyMemberView.as_view(), name='add-member'),


]