from django.shortcuts import render

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from users.models import UserDetail

class FacebookLoginView(APIView):
    permission_classes = [AllowAny]  # <-- Important!
    def post(self, request):
        access_token = request.data.get("access_token")

        # Verify token with Facebook
        fb_url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
        fb_response = requests.get(fb_url).json()

        if "error" in fb_response:
            return Response({"error": "Invalid Facebook token"}, status=400)

        fb_id = fb_response["id"]
        email = fb_response.get("email", f"{fb_id}@facebook.com")  # fallback if no email
        name = fb_response.get("name", "")
        #email = fb_response.get("email")
        print(name,email)

        # Check if user exists, else create
        user, _ = User.objects.get_or_create(username=fb_id, defaults={"email": email, "first_name": name})
        UserDetail.objects.get_or_create(user=user)

        # Generate JWT
        refresh = RefreshToken.for_user(user)
        print(refresh,name,refresh.access_token)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {"id": user.id, "name": user.first_name, "email": user.email}
        })
