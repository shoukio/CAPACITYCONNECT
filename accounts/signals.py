from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


ROLE_GROUP_NAMES = {value: label for value, label in Profile.Role.choices}


def sync_role_group(profile):
    role_group_name = ROLE_GROUP_NAMES[profile.role]
    role_group, _ = Group.objects.get_or_create(name=role_group_name)
    profile.user.groups.add(role_group)
    profile.user.groups.remove(
        *Group.objects.filter(name__in=ROLE_GROUP_NAMES.values()).exclude(
            pk=role_group.pk
        )
    )


@receiver(post_save, sender=get_user_model())
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        role = (
            Profile.Role.ADMINISTRATOR
            if instance.is_superuser
            else Profile.Role.LEARNER
        )
        Profile.objects.create(user=instance, role=role)


@receiver(post_save, sender=Profile)
def sync_profile_role_group(sender, instance, **kwargs):
    sync_role_group(instance)