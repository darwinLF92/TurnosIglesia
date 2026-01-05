from django import forms
from .models import Devoto

class DevotoForm(forms.ModelForm):
    class Meta:
        model = Devoto
        fields = ['cui_o_nit', 'nombre', 'correo', 'telefono', 'direccion', 'fecha_nacimiento', 'fotografia']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fotografia': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'capture': 'environment',  # Para abrir cámara trasera en móviles
                'class': 'form-control'
            }),
        }