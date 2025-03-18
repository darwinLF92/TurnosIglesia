from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import GroupStatus

@receiver(post_save, sender=Group)
def create_group_status(sender, instance, created, **kwargs):
    if created:
        GroupStatus.objects.create(group=instance, is_active=True)
