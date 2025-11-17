import random
from datetime import timedelta

from django.utils import timezone
from django.core.cache import cache
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
from accounts.send_sms import send_sms



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
    """
    API view to generate and send OTP via SMS.
    Prevents spam with caching and handles SMS delivery errors.
    """
    serializer_class = serializers.SendOTPSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def perform_create(self, serializer):
        phone = serializer.validated_data['phone_number']
        cache_key = f"otp_sent_{phone}"
        if cache.get(cache_key):
            raise ValidationError("لطفا چند ثانیه صبر کنید و دوباره تلاش کنید.")

        OTP.objects.filter(phone_number=phone, is_verified=False).update(expires_at=timezone.now())

        otp = OTP.objects.create(
            phone_number=phone,
            code=str(random.randint(100000, 999999)),
            expires_at=timezone.now() + timedelta(minutes=2)
        )

        text = f"کد تأیید شما: {otp.code}"

        cache.set(cache_key, True, timeout=60)

        success = send_sms(phone, text)
        if not success:
            raise ValidationError("ارسال پیامک با مشکل مواجه شد. لطفاً دوباره تلاش کنید.")


class VerifyOTPView(views.APIView):
    """
    API view to verify OTP codes.
    Validates attempts, marks OTP as used, and returns JWT tokens for the user.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        with transaction.atomic():
            otp = OTP.objects.select_for_update().filter(
                phone_number=phone, is_verified=False
            ).order_by('-created_at').first()

        if not otp:
            return Response({"error": "کد نامعتبر است"}, status=400)

        otp.increment_attempts()

        if not otp.can_attempt():
            return Response({"error": "تعداد تلاش‌های شما بیش از حد مجاز است. لطفاً کد جدید دریافت کنید."}, status=400)

        if otp.code != code:
            return Response({"error": "کد اشتباه است"}, status=400)

        otp.mark_used()

        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={'is_active': True}
        )
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": serializers.UserSerializer(user).data,
            "message": "Sign up" if created else "Sign in",
        })


class LogoutView(views.APIView):
    """
    API view to blacklist a refresh token and log out the user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"error": "توکن refresh ارسال نشده است."}, status=400)

        try:
            RefreshToken(token).blacklist()
            return Response({"message": "با موفقیت خارج شدید"}, status=200)
        except Exception:
            return Response({"error": "توکن نامعتبر یا از قبل باطل شده است."}, status=400)

