from django.db import models
from django.utils import timezone
from devotos.models import Devoto
from turnos.models import Turno

class RegistroInscripcion(models.Model):
    devoto = models.ForeignKey(Devoto, on_delete=models.CASCADE, related_name='inscripciones')
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    inscrito = models.BooleanField(default=True)
    entregado = models.BooleanField(default=False)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    valor_turno = models.DecimalField(max_digits=6, decimal_places=2)  # Se extrae del turno
    monto_pagado = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Cantidad pagada
    cambio = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Cambio calculado
    fecha_entrega_estimada = models.DateTimeField(blank=True, null=True)  # Nuevo campo
    lugar_entrega = models.CharField(max_length=255, blank=True, null=True)  # Nuevo campo

    def __str__(self):
        return f'{self.devoto.nombre} - Turno {self.turno.id}'

    def calcular_cambio(self):
        """Calcula el cambio si el devoto paga más del valor del turno."""
        self.cambio = max(self.monto_pagado - self.valor_turno, 0)
        return self.cambio

    def save(self, *args, **kwargs):
        """Antes de guardar, obtiene el valor del turno y calcula el cambio."""
        if self.turno:
            self.valor_turno = self.turno.valor  # Obtiene el precio desde el turno
        self.calcular_cambio()
        super().save(*args, **kwargs)

    def marcar_entregado(self):
        """Marca el turno como entregado y guarda la fecha."""
        self.entregado = True
        self.fecha_entrega = timezone.now()
        self.save()
