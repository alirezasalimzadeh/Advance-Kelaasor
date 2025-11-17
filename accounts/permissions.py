from rest_framework.permissions import BasePermission


class IsOwnerProfile(BasePermission):
    """
    Permission class that grants access only to the owner of the profile.
    Ensures that a user can view or modify their own profile but not others.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the profile belongs to the authenticated user
        return obj.user == request.user


class IsSuperAdmin(BasePermission):
    """Full access to everything."""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.is_superuser
                and request.user.is_staff
                and request.user.profile.has_role("super_admin")
        )


class IsSupportAdmin(BasePermission):
    """Access to support-related features (tickets, user help)."""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.is_staff
                and request.user.profile.has_role("support_admin")
        )


class IsFinancialAdmin(BasePermission):
    """Access to financial features (transactions, invoices)."""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.is_staff
                and request.user.profile.has_role("financial_admin")
        )


class IsEducationAdmin(BasePermission):
    """Access to education features (courses, enrollments)."""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.is_staff
                and request.user.profile.has_role("education_admin")
        )


class IsInstructor(BasePermission):
    """Access to instructor-only features (own courses, own students)."""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.is_active
                and request.user.profile.has_role("instructor")
        )


class IsStudent(BasePermission):
    """Access to student-only features (own profile, enrolled courses)."""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.is_active
                and request.user.profile.has_role("student")
        )


class IsGuest(BasePermission):
    """Access for non-authenticated users (public pages only)."""

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsSystem(BasePermission):
    """Access for system/internal tasks."""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.profile.has_role("system")
        )
