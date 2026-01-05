from django.db import models
from procesiones.models import Procesion



class Turno(models.Model):

    # 🔹 TIPOS DE TURNO
    TIPO_TURNO_CHOICES = (
        ('sin', 'Sin especificar'),
        ('caballeros', 'Caballeros'),
        ('damas', 'Damas'),
        ('infantil', 'Infantil'),
    )


    procesion = models.ForeignKey(
        Procesion,
        on_delete=models.CASCADE,
        related_name='turnos'
    )
    numero_turno = models.PositiveIntegerField()
    capacidad = models.PositiveIntegerField(default=32)
    valor = models.DecimalField(max_digits=6, decimal_places=2, default=25.00)
    activo = models.BooleanField(default=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    marcha_funebre = models.CharField(max_length=200, blank=True, null=True)
    # 👉 NUEVO CAMPO
    tipo_turno = models.CharField(
        max_length=20,
        choices=TIPO_TURNO_CHOICES,
        default='sin'
    )

    # 🔹 NUEVOS CAMPOS
    reservado_hermandad = models.BooleanField(
        default=False,
        help_text="Turno reservado completo para una hermandad visitante"
    )

    nombre_hermandad_visitante = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    # 👉 NUEVOS CAMPOS
    fecha_entrega = models.DateTimeField(
        "Fecha de entrega",
        blank=True,
        null=True
    )
    lugar_entrega = models.CharField(
        "Lugar de entrega",
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return f'Turno {self.numero_turno} - {self.procesion.nombre}'