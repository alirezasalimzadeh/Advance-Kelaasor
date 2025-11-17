from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts import models as user_models
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a UserProfile
    whenever a new User instance is created.
    """
    if created:
        user_models.UserProfile.objects.get_or_create(user=instance)
