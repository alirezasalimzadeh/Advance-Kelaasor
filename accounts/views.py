import random
from datetime import timedelta

from django.utils import timezone
from django.db import transaction

from rest_framework import generics, viewsets, views
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts import serializers
from accounts.models import User, Role, UserProfile, OTP
from accounts import permissions


class SuperAdminUserViewSet(viewsets.ModelViewSet):
    """
    Super admin has full CRUD access to all Users.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsSuperAdmin]


class SuperAdminRoleViewSet(viewsets.ModelViewSet):
    """
    Super admin has full CRUD access to all Roles.
    """
    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer
    permission_classes = [permissions.IsSuperAdmin]


class SuperAdminProfileViewSet(viewsets.ModelViewSet):
    """
    Super admin has full CRUD access to all profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = serializers.SuperAdminUserProfileSerializer
    permission_classes = [permissions.IsSuperAdmin]


class SupportAdminProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Support admin can only list and retrieve profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [permissions.IsSupportAdmin]


class FinancialAdminProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Financial admin can only list and retrieve profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [permissions.IsFinancialAdmin]


class EducationAdminProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Education admin can only list and retrieve profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [permissions.IsEducationAdmin]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Authenticated user can view and update their own profile.
    """
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class SendOTPView(CreateAPIView):
    serializer_class = serializers.SendOTPSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def perform_create(self, serializer):
        phone = serializer.validated_data['phone_number']
        OTP.objects.filter(phone_number=phone).delete()
        otp = OTP.objects.create(phone_number=phone,
                                 code=str(random.randint(100000, 999999)),
                                 expires_at=timezone.now() + timedelta(minutes=2))
        print(f"OTP for {otp.phone_number}: {otp.code}")


class VerifyOTPView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        otp = OTP.objects.filter(phone_number=phone, is_verified=False).last()

        if not otp:
            return Response({"error": "کد اشتباه یا نامعتبر است"}, status=400)

        otp.attempts += 1
        otp.save(update_fields=["attempts"])

        if otp.is_expired() or otp.code != code:
            if otp.attempts >= 5:
                return Response({"error": "تعداد تلاش‌های شما بیش از حد مجاز است. لطفاً کد جدید دریافت کنید."},
                                status=400)
            return Response({"error": "کد اشتباه یا نامعتبر است"}, status=400)

        otp.mark_used()
        user, created = User.objects.get_or_create(phone_number=phone)
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": serializers.UserSerializer(user).data,
            "message": "Sign up" if created else "Sign in",
        })

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "با موفقیت خارج شدید"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)