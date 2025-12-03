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
    profile_image = serializers.SerializerMethodField()
    class Meta:
        model = UserDetail
        fields = ["id","user","profile_image"]
    def get_profile_image(self, obj):
        if obj.profile:
            try:
                return obj.profile.url
            except:
                pass
        if obj.profile_url:
                    return obj.profile_url


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    family = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()



    class Meta:
        model = UserDetail
        fields = ["user",  "profile_image", "family", "member_count","phone_number"]

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
    def get_profile_image(self, obj):

        if obj.profile:
            try:
                return obj.profile.url
            except:
                pass

        if obj.profile_url:
            return obj.profile_url



class EditProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30,required=True)
    last_name = serializers.CharField(max_length=30,required=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(max_length=10,required=False)
    profile_image = serializers.ImageField(required=False)




