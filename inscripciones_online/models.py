from django.conf import settings
from django.db import models
from devotos.models import Devoto
from turnos.models import Turno

class DevotoCuenta(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devoto_cuenta")
    devoto = models.OneToOneField(Devoto, on_delete=models.CASCADE, related_name="cuenta")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.devoto.nombre}"


class TurnoAcceso(models.Model):
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE, related_name="acceso")
    password_turno = models.CharField(max_length=50)  # contraseña/clave a enviar por WhatsApp

    # Entrega (puede ser por procesión o por turno; aquí lo dejamos por turno)
    fecha_entrega_estimada = models.DateTimeField(blank=True, null=True)
    lugar_entrega = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Acceso Turno {self.turno.numero_turno} - {self.turno.procesion.nombre}"