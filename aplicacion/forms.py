from django import forms
from .models import Informacion, HistoriaImagen, Multimedia, MarchaFunebre, RecorridoProcesional, Oracion, ConfiguracionHome, ImagenPresentacion

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