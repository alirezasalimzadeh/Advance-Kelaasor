"""
Accounts app models.

Defines custom User model (with phone_number as login field),
UserProfile for extended personal details and roles,
Role model for flexible role management,
and OTP model for send sms code.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django_jalali.db import models as jmodels

from accounts.user_managers import UserManager
from accounts.validator import validate_phone_number


class User(AbstractUser):
    """
    Custom User model using phone_number as the unique identifier.
    Replaces default username/email fields and integrates with UserManager.
    """
    username = None
    first_name = None
    last_name = None
    email = None
    phone_number = models.CharField(max_length=11, unique=True, validators=[validate_phone_number])

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    # def get_cart(self):
    #     cart, _ = Cart.objects.get_or_create(user=self)
    #     return cart

    def __str__(self):
        return self.phone_number


class Role(models.Model):
    """
    Role model for defining user roles.
    Supports flexible assignment via ManyToMany in UserProfile.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Extended profile model linked to User.
    Stores personal details, roles, and optional information.
    Provides helpers to check profile completeness and missing fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    roles = models.ManyToManyField(Role, related_name="users")
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    national_id = models.CharField(max_length=10, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)

    avatar = models.ImageField(upload_to="profiles/avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)

    job_title = models.CharField(max_length=100, blank=True)
    birth_date = jmodels.jDateField(null=True, blank=True)
    province = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    membership_date = jmodels.jDateField(auto_now_add=True)

    @property
    def full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}".strip()

    @property
    def is_complete(self):
        """
        Check if the profile has all required mandatory fields filled.
        """
        required_fields = [self.first_name, self.last_name, self.email, self.national_id]
        return all(required_fields)

    def incomplete_fields(self):
        """
        Return a list of required fields that are missing.
        Useful for showing the user what to complete.
        """
        missing = []
        if not self.first_name:
            missing.append("first_name")
        if not self.last_name:
            missing.append("last_name")
        if not self.email:
            missing.append("email")
        if not self.national_id:
            missing.append("national_id")
        return missing

    def get_roles(self):
        """
        Return a list of role names assigned to the user.
        """
        return list(self.roles.values_list("name", flat=True))

    def has_role(self, role_name: str) -> bool:
        """
        Return True if the user has the given role, otherwise False.
        """
        return self.roles.filter(name=role_name).exists()

    def __str__(self):
        full_name = self.full_name if self.full_name else self.user.phone_number
        roles = ", ".join(self.get_roles()) if self.roles.exists() else "No roles"
        return f"{full_name} ({roles})"


class OTP(models.Model):
    phone_number = models.CharField(max_length=11, db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at or self.attempts >= 5

    def mark_used(self):
        self.is_verified = True
        self.save(update_fields=["is_verified"])

    def __str__(self):
        return f"OTP for {self.phone_number} ({'used' if self.is_verified else 'not used'})"
