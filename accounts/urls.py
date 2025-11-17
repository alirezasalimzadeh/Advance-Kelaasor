from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SuperAdminUserViewSet,
    SuperAdminRoleViewSet,
    SuperAdminProfileViewSet,
    SupportAdminProfileViewSet,
    FinancialAdminProfileViewSet,
    EducationAdminProfileViewSet,
    UserProfileView,
)

router = DefaultRouter()
router.register(r'super-admin/users', SuperAdminUserViewSet, basename='super-admin-users')
router.register(r'super-admin/roles', SuperAdminRoleViewSet, basename='super-admin-roles')
router.register(r'super-admin/profiles', SuperAdminProfileViewSet, basename='super-admin-profiles')
router.register(r'support-admin/profiles', SupportAdminProfileViewSet, basename='support-admin-profiles')
router.register(r'financial-admin/profiles', FinancialAdminProfileViewSet, basename='financial-admin-profiles')
router.register(r'education-admin/profiles', EducationAdminProfileViewSet, basename='education-admin-profiles')

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    path('', include(router.urls)),
]
