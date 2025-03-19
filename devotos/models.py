from django.db import models
from django.conf import settings
from django.utils import timezone

class Devoto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10, editable=False, unique=True, null=True)
    edad = models.PositiveIntegerField()
    cui_o_nit = models.CharField(max_length=15, unique=True, blank=True, null=True)
    activo = models.BooleanField(default=True)

    fecha_nacimiento = models.DateField(blank=True, null=True)
    fotografia = models.ImageField(upload_to='fotografias_devotos/', blank=True, null=True)

    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devotos_registrados"
    )
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devotos_modificados"
    )
    fecha_modificacion = models.DateTimeField(null=True, blank=True)
    usuario_eliminacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devotos_eliminados"
    )
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Agregar código de país si no lo tiene
        if self.telefono and not self.telefono.startswith('+502'):
            self.telefono = f'+502{self.telefono.strip()}'

        # Asignar código automático si no existe
        if not self.codigo:
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

