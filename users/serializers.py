from rest_framework import serializers
from .models import UserDetail
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserDetail
        fields = ["id","user","profile","profile_url"]
