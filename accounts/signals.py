from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from accounts import models as user_models

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_models.UserProfile.objects.get_or_create(user=instance)
