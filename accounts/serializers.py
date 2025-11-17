from rest_framework import serializers
from .models import User, Role, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Only exposes phone_number since login is based on it.
    """

    class Meta:
        model = User
        fields = ["id", "phone_number"]


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.
    """

    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class SuperAdminUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    Includes personal information and related roles.
    """
    user = UserSerializer(read_only=True)  # show user info
    roles = serializers.PrimaryKeyRelatedField(many=True,
                                               queryset=Role.objects.all())  # super admin can change roles
    roles_detail = RoleSerializer(many=True, read_only=True, source="roles")
    birth_date = serializers.DateField(format="%Y/%m/%d", required=False)
    membership_date = serializers.DateField(format="%Y/%m/%d", read_only=True)
    avatar = serializers.ImageField(use_url=True, required=False)
    is_complete = serializers.BooleanField(read_only=True)  # derived from model method
    incomplete_fields = serializers.ListField(child=serializers.CharField(), read_only=True)  # list of missing fields

    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    Includes personal information and related roles.
    """
    user = UserSerializer(read_only=True)  # show user info
    roles = RoleSerializer(many=True, read_only=True)   # show roles
    birth_date = serializers.DateField(format="%Y/%m/%d", required=False)
    membership_date = serializers.DateField(format="%Y/%m/%d", read_only=True)
    avatar = serializers.ImageField(use_url=True, required=False)
    is_complete = serializers.BooleanField(read_only=True)  # derived from model method
    incomplete_fields = serializers.ListField(child=serializers.CharField(), read_only=True)  # list of missing fields

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ["membership_date", "roles"]
