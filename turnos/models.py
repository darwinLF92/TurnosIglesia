from django.db import models
from procesiones.models import Procesion



class Turno(models.Model):
    procesion = models.ForeignKey(Procesion, on_delete=models.CASCADE, related_name='turnos')
    numero_turno = models.PositiveIntegerField()  # Turnos numerados del 1 al 16
    capacidad = models.PositiveIntegerField(default=32)
    valor = models.DecimalField(max_digits=6, decimal_places=2, default=25.00)
    activo = models.BooleanField(default=True)  # Añadir este campo si no existe
    referencia = models.CharField(max_length=100, blank=True, null=True)
    marcha_funebre = models.CharField(max_length=60, blank=True, null=True)

    def __str__(self):
        return f'Turno {self.numero_turno} - Procesión {self.procesion.nombre}'
