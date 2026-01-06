from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import GroupStatus
from .models import UserProfile
from django.contrib.auth.models import User

@receiver(post_save, sender=Group)
def create_group_status(sender, instance, created, **kwargs):
    if created:
        GroupStatus.objects.create(group=instance, is_active=True)

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    try:
        instance.perfil.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


