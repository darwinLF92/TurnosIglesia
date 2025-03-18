from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
# Modelo para "¿Quiénes somos?"
class Informacion(models.Model):
    titulo = models.CharField(max_length=255, default="¿Quiénes somos?")
    contenido = models.TextField()

    def __str__(self):
        return self.titulo


# Modelo para "Historia de nuestras imágenes"
class HistoriaImagen(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='historias_imagenes/')

    def __str__(self):
        return self.titulo


# Modelo para "Fototeca y Multimedia"
class Multimedia(models.Model):
    titulo = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100, choices=(('imagen', 'Imagen'), ('video', 'Video')))
    archivo = models.FileField(upload_to='fototeca_multimedia/')

    def __str__(self):
        return self.titulo


# Modelo para "Marchas Fúnebres"
class MarchaFunebre(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    audio = models.FileField(upload_to='marchas_funebres/')
    duracion = models.CharField(max_length=10, blank=True, null=True, help_text="Ejemplo: 5:30")
    favoritos = models.PositiveIntegerField(default=0, help_text="Contador de favoritos o me gusta")
    imagen_portada = models.ImageField(
        upload_to='imagenes_marchas/',
        blank=True,
        null=True,
        help_text="Opcional. Imagen que se mostrará como portada de la marcha."
    )
    me_gusta = models.PositiveIntegerField(default=0)
    fecha_subida = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titulo
    

class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    marcha = models.ForeignKey(MarchaFunebre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'marcha')  # Evita favoritos duplicados

    def __str__(self):
        return f"{self.usuario.username} ❤️ {self.marcha.titulo}"


# Modelo para "Recorridos Procesionales"
class RecorridoProcesional(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='recorridos_procesionales/')

    def __str__(self):
        return self.titulo


# Modelo para "Oraciones"
class Oracion(models.Model):
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='oraciones/', blank=True, null=True)

    def __str__(self):
        return self.titulo
    
class ConfiguracionHome(models.Model):
    SECCIONES = [
        ('quienes_somos', '¿Quiénes somos?'),
        ('historia_imagenes', 'Historia de nuestras imágenes'),
        ('fototeca_multimedia', 'Fototeca y Multimedia'),
        ('marchas_funebres', 'Marchas Fúnebres'),
        ('recorridos_procesionales', 'Recorridos Procesionales'),
        ('oraciones', 'Oraciones'),
    ]

    seccion = models.CharField(max_length=50, choices=SECCIONES, unique=True)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
    

class ImagenInformacion(models.Model):
    informacion = models.ForeignKey(
        Informacion,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='informacion/')

    def __str__(self):
        return f"Imagen de {self.informacion.titulo}"
class ImagenPresentacion(models.Model):
    titulo = models.CharField(max_length=255, blank=True, null=True)
    imagen = models.ImageField(upload_to='imagenes_presentacion/')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo if self.titulo else f"Imagen {self.id}"

