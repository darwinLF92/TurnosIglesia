from django.db import models
from django.utils import timezone
from devotos.models import Devoto
from turnos.models import Turno

class RegistroInscripcion(models.Model):
    devoto = models.ForeignKey(Devoto, on_delete=models.CASCADE, related_name='inscripciones')
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    inscrito = models.BooleanField(default=False)
    entregado = models.BooleanField(default=False)
    fecha_entrega = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.participante.nombre} - Turno {self.turno.numero_turno}'
    
    def marcar_entregado(self):
        self.entregado = True
        self.fecha_entrega = timezone.now()
        self.save()
