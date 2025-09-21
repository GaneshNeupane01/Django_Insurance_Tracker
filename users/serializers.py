from rest_framework import serializers
from .models import UserDetail
from django.contrib.auth.models import User
from families.serializers import FamilySerializer
from familymember.models import FamilyMember



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserDetail
        fields = ["id","user","profile","profile_url"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    family = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = UserDetail
        fields = ["user", "profile", "profile_url", "family", "member_count"]

    def get_family(self, obj):
        family_member = FamilyMember.objects.filter(user=obj).first()
        if family_member:

            return FamilySerializer(family_member.family).data
        return None

    def get_member_count(self, obj):
        family_member = FamilyMember.objects.filter(user=obj).first()
        if family_member:
            return FamilyMember.objects.filter(family=family_member.family).count()
        return 0

