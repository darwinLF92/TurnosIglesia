# usuarios/models.py
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )

    cui = models.CharField("CUI", max_length=20, unique=True, blank=True, null=True)
    nombres = models.CharField("Nombres", max_length=100, blank=True, null=True)
    apellidos = models.CharField("Apellidos", max_length=100, blank=True, null=True)
    direccion = models.CharField("Dirección", max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField("Fecha de nacimiento", blank=True, null=True)
    estatura = models.PositiveIntegerField(
    "Estatura (cm)",
    blank=True,
    null=True
    )
    telefono = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    correo_verificado = models.BooleanField("Correo verificado", default=False)
    estado = models.BooleanField("Activo", default=True)
    foto_perfil = models.ImageField(
        upload_to="fotos_perfil/",   # se guardarán en MEDIA_ROOT/fotos_perfil/
        blank=True,
        null=True,
        verbose_name="Foto de perfil"
    )

    def __str__(self):
        return f"{self.nombres or ''} {self.apellidos or ''} ({self.user.username})"



class GroupStatus(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.group.name} - {'Active' if self.is_active else 'Inactive'}"
