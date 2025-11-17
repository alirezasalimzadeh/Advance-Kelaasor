from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts import views

router = DefaultRouter()
router.register(r'super-admin/users', views.SuperAdminUserViewSet, basename='super-admin-users')
router.register(r'super-admin/roles', views.SuperAdminRoleViewSet, basename='super-admin-roles')
router.register(r'super-admin/profiles', views.SuperAdminProfileViewSet, basename='super-admin-profiles')
router.register(r'support-admin/profiles', views.SupportAdminProfileViewSet, basename='support-admin-profiles')
router.register(r'financial-admin/profiles', views.FinancialAdminProfileViewSet, basename='financial-admin-profiles')
router.register(r'education-admin/profiles', views.EducationAdminProfileViewSet, basename='education-admin-profiles')

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),

    path("auth/otp/send/", views.SendOTPView.as_view(), name="send-otp"),

    path("auth/otp/verify/", views.VerifyOTPView.as_view(), name="verify-otp"),

    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('', include(router.urls)),
]
