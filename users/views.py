from django.shortcuts import render

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from users.models import UserDetail
from .serializers import ProfileSerializer
from rest_framework.decorators import api_view
from familymember.models import FamilyMember
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from reminder.models import Reminder
from reminder.serializers import ReminderSerializer
from .serializers import EditProfileSerializer


from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = "211644975621-ohulp5rj1oc326guejk6fc00tcn0tg29.apps.googleusercontent.com"

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("api called for google")
        token = request.data.get("id_token")
        try:
            # Verify Google ID token
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

            google_id = idinfo["sub"]
            email = idinfo.get("email", f"{google_id}@google.com")
            name = idinfo.get("name", "")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")
            picture_url = idinfo.get("picture", "")

            # Create or get user
            user, created = User.objects.get_or_create(username=google_id, defaults={"email": email, "first_name": first_name, "last_name": last_name})
            user_detail, _ = UserDetail.objects.get_or_create(user=user)
            isFirstLogin = False

            if created or not user_detail.profile_url:
                isFirstLogin = True
                user_detail.profile_url = picture_url
                user_detail.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {"id": user.id, "name": user.first_name, "email": user.email, "profile_url": user_detail.profile_url},
                "isFirstLogin": isFirstLogin
            })

        except ValueError:
            return Response({"error": "Invalid Google token"}, status=400)








class FacebookLoginView(APIView):
    permission_classes = [AllowAny]  # <-- Important!
    def post(self, request):
        access_token = request.data.get("access_token")

        # Verify token with Facebook
        fb_url = f"https://graph.facebook.com/me?fields=id,first_name,last_name,name,email,picture.type(large)&access_token={access_token}"
        fb_response = requests.get(fb_url).json()

        if "error" in fb_response:
            return Response({"error": "Invalid Facebook token"}, status=400)

        fb_id = fb_response["id"]
        email = fb_response.get("email", f"{fb_id}@facebook.com")  # fallback if no email
        name = fb_response.get("name", "")
        first_name = fb_response.get("first_name", "")
        last_name = fb_response.get("last_name", "")
        #email = fb_response.get("email")
        print(name,email,first_name,last_name)
        #picture_url = fb_response["picture"]["data"]["url"]
        profile_url = f"https://graph.facebook.com/{fb_id}/picture?type=large"



        # Check if user exists, else create
        user, created = User.objects.get_or_create(username=fb_id, defaults={"email": email, "first_name": first_name, "last_name": last_name})
        user_detail, _ = UserDetail.objects.get_or_create(user=user)
        isFirstLogin = False
        if created or not user_detail.profile_url:
            isFirstLogin = True
            user_detail.profile_url = profile_url
            user_detail.save()
        print(profile_url)
        # Generate JWT
        refresh = RefreshToken.for_user(user)
        print(refresh,name,refresh.access_token)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {"id": user.id, "name": user.first_name, "email": user.email},
            "isFirstLogin": isFirstLogin
        })


class ProfileView(APIView):
    def get(self,request):
        user = request.user
        user_detail = UserDetail.objects.get(user=user)
        member = FamilyMember.objects.get(user=user_detail)

        vehicles = Vehicle.objects.filter(family_member=member)

        reminders = Reminder.objects.filter(family_member=member)

        reminders = ReminderSerializer(reminders, many=True).data

        vehicles = VehicleSerializer(vehicles, many=True).data
        user_detail = ProfileSerializer(user_detail).data
        print(reminders,vehicles,user_detail)

        return Response({
            "user_detail": user_detail,
            "vehicles": vehicles,
            "reminders": reminders
        })



@api_view(['GET'])
def get_user(request):
    user = request.user
    user_detail = UserDetail.objects.get(user=user)
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    if user_detail.profile:
        image = user_detail.profile
    else:
        if user_detail.profile_url:
            image = user_detail.profile_url
        else:
            image = None


    return Response({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "profile_image": image
    })

@api_view(['POST'])
def edit_profile(request):
    user = request.user
    user_detail = UserDetail.objects.get(user=user)
    serializer = EditProfileSerializer(data=request.data)
    if serializer.is_valid():
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        profile_image = serializer.validated_data.get('profile_image')
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        if phone_number:
            user_detail.phone_number = phone_number
        if profile_image:
            user_detail.profile = profile_image
        user.save()
        user_detail.save()
        return Response({'message': 'Profile updated successfully'})