from django import forms
from .models import Informacion, HistoriaImagen, Multimedia, MarchaFunebre, RecorridoProcesional, Oracion, ConfiguracionHome, ImagenPresentacion
from .models import MediaAlbum, Foto, Video
class InformacionForm(forms.ModelForm):
    class Meta:
        model = Informacion
        fields = ['titulo', 'contenido']


class HistoriaImagenForm(forms.ModelForm):
    class Meta:
        model = HistoriaImagen
        fields = ['titulo', 'descripcion', 'imagen']


class MultimediaForm(forms.ModelForm):
    class Meta:
        model = Multimedia
        fields = ['titulo', 'categoria', 'archivo']


class MarchaFunebreForm(forms.ModelForm):
    class Meta:
        model = MarchaFunebre
        fields = ['titulo', 'descripcion', 'audio']


class RecorridoProcesionalForm(forms.ModelForm):
    class Meta:
        model = RecorridoProcesional
        fields = ['titulo', 'descripcion', 'imagen']


class OracionForm(forms.ModelForm):
    class Meta:
        model = Oracion
        fields = ['titulo', 'contenido', 'imagen']

class ConfiguracionHomeForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionHome
        fields = ['seccion', 'titulo', 'descripcion', 'activo']
        widgets = {
            'seccion': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ImagenPresentacionForm(forms.ModelForm):
    class Meta:
        model = ImagenPresentacion
        fields = ['titulo', 'imagen', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MarchaFunebreForm(forms.ModelForm):
    class Meta:
        model = MarchaFunebre
        fields = ['titulo', 'descripcion', 'audio', 'imagen_portada', 'duracion']


class MediaAlbumForm(forms.ModelForm):
    class Meta:
        model = MediaAlbum
        fields = ['titulo', 'descripcion', 'tipo', 'portada', 'activo', 'orden']

# >>> Widget para múltiples archivos
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class FotoBulkUploadForm(forms.Form):
    # el nombre "imagenes" lo usas en la vista con request.FILES.getlist('imagenes')
    imagenes = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        required=True,
        help_text='Puedes seleccionar varias imágenes.'
    )

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['titulo', 'url', 'archivo', 'miniatura']
        help_texts = {
            'url': 'Pega un enlace de YouTube/Vimeo/Facebook. Deja vacío si adjuntas archivo.',
            'archivo': 'Sube un MP4/WebM. Deja vacío si usas URL.',
            'miniatura': 'Opcional: imagen a usar como portada del video.',
        }

class FotoForm(forms.ModelForm):
    # que la imagen NO sea obligatoria al editar (por si no la reemplazan)
    imagen = forms.ImageField(required=False)

    class Meta:
        model = Foto
        fields = ['titulo', 'imagen']

class VideoForm2(forms.ModelForm):
    # url/archivo opcionales aquí; validamos abajo
    url = forms.URLField(required=False)
    archivo = forms.FileField(required=False)
    miniatura = forms.ImageField(required=False)

    class Meta:
        model = Video
        fields = ['titulo', 'url', 'archivo', 'miniatura']
        help_texts = {
            'url': 'Pega un enlace (YouTube/Vimeo/Facebook). Deja vacío si adjuntas archivo.',
            'archivo': 'Sube un MP4/WebM. Deja vacío si usas URL.',
            'miniatura': 'Opcional: imagen portada para videos locales o externos.',
        }

    def clean(self):
        cleaned = super().clean()
        url = cleaned.get('url')
        archivo = cleaned.get('archivo')

        # Si estamos editando y no enviaron campos, usamos los que ya existen
        inst = self.instance

        has_url = bool(url or (inst and inst.url))
        has_file = bool(archivo or (inst and inst.archivo))

        if not has_url and not has_file:
            self.add_error('url', 'Debes proporcionar una URL o un archivo.')
            self.add_error('archivo', 'Debes proporcionar una URL o un archivo.')
        if url and archivo:
            self.add_error('url', 'Proporciona solo URL o solo archivo.')
            self.add_error('archivo', 'Proporciona solo URL o solo archivo.')

        return cleaned