
from families.models import Family

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import VehicleSerializer
from familymember.models import FamilyMember
from vehicles.models import Vehicle
from users.models import UserDetail
from reminder.models import Reminder
from insurance.models import Insurance

# Create your views here.

class VehicleListView(APIView):
    print('api called successfully')
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_detail = UserDetail.objects.get(user=request.user)
        member = FamilyMember.objects.get(user=user_detail)


        family_members = FamilyMember.objects.filter(family=member.family)

        vehicles = Vehicle.objects.filter(family_member__in=family_members)

        serializer = VehicleSerializer(vehicles, many=True)
        print(serializer.data)

        return Response(serializer.data)
