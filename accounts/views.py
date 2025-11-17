from rest_framework import viewsets
from rest_framework import generics, permissions
from accounts.serializers import UserSerializer, RoleSerializer, SuperAdminUserProfileSerializer, UserProfileSerializer
from accounts.models import User, Role, UserProfile

from .permissions import (
    IsSuperAdmin,
    IsSupportAdmin,
    IsFinancialAdmin,
    IsEducationAdmin,
    IsInstructor,
    IsStudent,
    IsGuest,
    IsSystem,
)


class SuperAdminUserViewSet(viewsets.ModelViewSet):
    """
    Super admin has full CRUD access to all Users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]


class SuperAdminRoleViewSet(viewsets.ModelViewSet):
    """
    Super admin has full CRUD access to all Roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsSuperAdmin]


class SuperAdminProfileViewSet(viewsets.ModelViewSet):
    """
    Super admin has full CRUD access to all profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = SuperAdminUserProfileSerializer
    permission_classes = [IsSuperAdmin]


class SupportAdminProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Support admin can only list and retrieve profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsSupportAdmin]


class FinancialAdminProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Financial admin can only list and retrieve profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsFinancialAdmin]


class EducationAdminProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Education admin can only list and retrieve profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsEducationAdmin]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Authenticated user can view and update their own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
