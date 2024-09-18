from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Devoto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10, editable=False, unique=True, null=True)  # Temporarily allow null
    edad = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if not self.codigo:  # Si el código no está establecido
            last_devoto = Devoto.objects.exclude(pk=self.pk).order_by('codigo').last()
            if last_devoto and last_devoto.codigo:
                last_number = int(last_devoto.codigo.replace('C', ''))
                new_number = last_number + 1
                self.codigo = 'C' + str(new_number).zfill(7)
            else:
                self.codigo = 'C0000001'
        super(Devoto, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre
