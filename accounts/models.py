"""
Accounts app models.

Defines custom User model (with phone_number as login field),
UserProfile for extended personal details and roles,
and Role model for flexible role management.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from accounts.user_managers import UserManager


class User(AbstractUser):
    """
    Custom User model using phone_number as the unique identifier.
    Replaces default username/email fields and integrates with UserManager.
    """
    username = None
    first_name = None
    last_name = None
    email = None
    phone_number = models.CharField(max_length=11, unique=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    # def get_cart(self):
    #     cart, _ = Cart.objects.get_or_create(user=self)
    #     return cart

    def __str__(self):
        return self.phone_number


