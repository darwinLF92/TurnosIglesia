from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from urllib.parse import urlencode, urlparse, parse_qs, quote

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
    
class HistoriaImagen(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='historia_imagenes/')
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)   # para ordenar manualmente
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', '-fecha_creacion']

    def __str__(self):
        return self.titulo

class MediaAlbum(models.Model):
    FOTO = 'foto'
    VIDEO = 'video'
    TIPOS = [(FOTO, 'Fotografías'), (VIDEO, 'Videos')]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    portada = models.ImageField(upload_to='albumes/portadas/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', '-creado']

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.titulo}'


class Foto(models.Model):
    album = models.ForeignKey(MediaAlbum, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='albumes/fotos/')
    titulo = models.CharField(max_length=200, blank=True)

    def clean(self):
        if self.album and self.album.tipo != MediaAlbum.FOTO:
            raise ValidationError('Solo puedes subir fotos a álbumes de tipo Fotografías.')

    def __str__(self):
        return self.titulo or f'Foto #{self.pk}'


class Video(models.Model):
    album = models.ForeignKey(MediaAlbum, on_delete=models.CASCADE, related_name='videos')
    titulo = models.CharField(max_length=200, blank=True)
    # puedes admitir URL (YouTube/Vimeo) o archivo subido
    url = models.URLField(blank=True)
    archivo = models.FileField(upload_to='albumes/videos/', blank=True, null=True)
    creado  = models.DateTimeField(auto_now_add=True)
    miniatura = models.ImageField(upload_to='albumes/video_posters/', blank=True, null=True)  # opcional
    
    def clean(self):
        if not self.url and not self.archivo:
            raise ValidationError('Debes proporcionar una URL o un archivo de video.')
        if self.url and self.archivo:
            raise ValidationError('Proporciona solo URL o solo archivo, no ambos.')

    # --- URL de embed para iframe (ya la usabas) ---
    def embed_src(self):
        u = (self.url or '').strip()
        if not u: return ''
        # YouTube
        if 'youtube.com/watch' in u or 'youtu.be/' in u:
            vid = self.youtube_id()
            return f'https://www.youtube.com/embed/{vid}' if vid else u
        # Vimeo
        if 'vimeo.com/' in u and 'player.vimeo.com' not in u:
            vid = u.rstrip('/').split('/')[-1]
            return f'https://player.vimeo.com/video/{vid}'
        # Facebook
        if 'facebook.com/' in u:
            base = 'https://www.facebook.com/plugins/video.php'
            qs = urlencode({'href': u, 'show_text': 0, 'width': 1280})
            return f'{base}?{qs}'
        return u

    # --- Helpers para miniaturas ---
    def youtube_id(self):
        u = (self.url or '').strip()
        if 'watch' in u:
            return parse_qs(urlparse(u).query).get('v', [''])[0]
        if 'youtu.be/' in u:
            return u.rstrip('/').split('/')[-1]
        return ''

    def thumbnail_url(self):
        """URL de imagen para mostrar en la grilla."""
        # 1) Si subieron miniatura manual
        if self.miniatura:
            try:
                return self.miniatura.url
            except Exception:
                pass
        # 2) Si es YouTube
        yid = self.youtube_id()
        if yid:
            return f'https://img.youtube.com/vi/{yid}/hqdefault.jpg'
        # 3) Si es Vimeo (servicio público de thumbs)
        u = (self.url or '')
        if 'vimeo.com/' in u:
            vid = u.rstrip('/').split('/')[-1]
            return f'https://vumbnail.com/{vid}.jpg'
        # 4) Sin suerte → None (usa placeholder en template)
        return ''