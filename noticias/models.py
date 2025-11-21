from django.conf import settings
from django.db import models
from django.utils import timezone

from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import os
import subprocess
from django.urls import reverse

class Post(models.Model):
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts_noticias'
    )
    contenido = models.TextField(blank=True)
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    # likes como ManyToMany para simplificar
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='likes_noticias',
        blank=True
    )

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"Post de {self.autor} - {self.creado_en:%d/%m/%Y %H:%M}"

    @property
    def total_likes(self):
        return self.likes.count()


class PostMedia(models.Model):
    TIPO_MEDIA = (
        ('imagen', 'Imagen'),
        ('video', 'Video'),
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='medios'
    )
    archivo = models.FileField(upload_to='noticias/')
    tipo = models.CharField(max_length=10, choices=TIPO_MEDIA)
    orden = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tipo} para Post {self.post_id}"

    def save(self, *args, **kwargs):
        """
        Solo convierte IMÁGENES a WEBP.
        Videos se guardan sin modificar.
        """
        super_guardar = super().save

        nombre, extension = os.path.splitext(self.archivo.name)
        extension = extension.lower()

        # Si es imagen, convertir a webp si no lo es aún
        if self.tipo == 'imagen':
            if extension not in ['.webp']:
                self._convertir_imagen_a_webp()

        # Guardar luego de la posible conversión
        super_guardar(*args, **kwargs)

    def _convertir_imagen_a_webp(self):
        """Convierte cualquier imagen (jpg, png, etc.) a un archivo WEBP optimizado."""
        try:
            img = Image.open(self.archivo)
            img = img.convert('RGB')  # evita problemas de transparencia

            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=80)
            buffer.seek(0)

            nuevo_nombre = os.path.splitext(self.archivo.name)[0] + '.webp'
            self.archivo = ContentFile(buffer.read(), name=nuevo_nombre)

        except Exception as e:
            print("Error convirtiendo a WEBP:", e)
            # Si falla, se deja el archivo original
            pass


class Comentario(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios_noticias'
    )
    texto = models.TextField()
    creado_en = models.DateTimeField(default=timezone.now)

    # ⭐ NUEVO: Likes en comentarios
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='likes_comentarios',
        blank=True
    )

    # ⭐ NUEVO: Respuestas a comentarios (estructura tipo Facebook)
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='respuestas'
    )

    class Meta:
        ordering = ['creado_en']

    def __str__(self):
        return f"Comentario de {self.autor} en Post {self.post_id}"

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def es_respuesta(self):
        return self.padre is not None


class Notificacion(models.Model):
    TIPOS = (
        ('like_post', 'Me gusta en tu publicación'),
        ('comentario_post', 'Comentario en tu publicación'),
        ('respuesta_comentario', 'Respuesta a tu comentario'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=30, choices=TIPOS)
    texto = models.CharField(max_length=255)
    post = models.ForeignKey(
        'noticias.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones'
    )
    comentario = models.ForeignKey(
        'noticias.Comentario',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"Notif para {self.usuario} - {self.tipo}"

    def get_url(self):
            # Redirige al muro con un anchor al post
            return reverse('noticias:muro') + f"#post-{self.post.id}"