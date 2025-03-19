from django.db import models
from django.utils import timezone
from devotos.models import Devoto
from turnos.models import Turno

class RegistroInscripcion(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)  # ← Nuevo campo personalizado

    devoto = models.ForeignKey(Devoto, on_delete=models.CASCADE, related_name='inscripciones')
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    inscrito = models.BooleanField(default=True)
    entregado = models.BooleanField(default=False)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    valor_turno = models.DecimalField(max_digits=6, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    cambio = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    fecha_entrega_estimada = models.DateTimeField(blank=True, null=True)
    lugar_entrega = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.codigo if self.codigo else f'{self.devoto.nombre} - Turno {self.turno.id}'

    def calcular_cambio(self):
        self.cambio = max(self.monto_pagado - self.valor_turno, 0)
        return self.cambio

    def save(self, *args, **kwargs):
        if self.turno:
            self.valor_turno = self.turno.valor
        self.calcular_cambio()

        # Generar código solo si no existe
        if not self.codigo:
            ultimo = RegistroInscripcion.objects.order_by('-id').first()
            if ultimo and ultimo.codigo and ultimo.codigo.startswith('HSVD-'):
                numero_actual = int(ultimo.codigo.replace('HSVD-', ''))
                nuevo_numero = numero_actual + 1
            else:
                nuevo_numero = 1001001  # Valor inicial

            self.codigo = f'HSVD-{nuevo_numero}'

        super().save(*args, **kwargs)

    def marcar_entregado(self):
        self.entregado = True
        self.fecha_entrega = timezone.now()
        self.save()

