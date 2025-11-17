from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from accounts.models import User, Role, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model using phone_number as login field.
    """
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2"),
        }),
    )
    list_display = ("id", "phone_number", "is_staff", "is_active")
    search_fields = ("phone_number",)
    ordering = ("id",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin for Role model.
    """
    list_display = ("id", "name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin for UserProfile model.
    """
    list_display = ("id", "user", "full_name", "is_complete", "get_roles_display")
    search_fields = ("user__phone_number", "first_name", "last_name", "email", "national_id")
    list_filter = ("province", "city", "roles")
    ordering = ("id",)

    def get_roles_display(self, obj):
        return ", ".join(obj.get_roles()) if obj.roles.exists() else "-"
    get_roles_display.short_description = "Roles"
