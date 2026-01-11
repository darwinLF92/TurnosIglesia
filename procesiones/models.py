from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Procesion(models.Model):
    nombre = models.CharField(max_length=200)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)

    activo = models.BooleanField(default=True)

    # 👉 NUEVOS CAMPOS
    es_relevante = models.BooleanField(
        default=False,
        help_text="Marca esta procesión para mostrarla en el home"
    )

    imagen_promocional = models.ImageField(
        upload_to="procesiones/promocion/",
        blank=True,
        null=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    turnos_devoto_online = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad máxima de turnos online por devoto (0 = ilimitado)"
    )

    turnos_devoto_local = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad máxima de turnos presenciales por devoto (0 = ilimitado)"
    )


    def __str__(self):
        return self.nombre