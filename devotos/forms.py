from django import forms
from .models import Devoto

class DevotoForm(forms.ModelForm):
    class Meta:
        model = Devoto
        fields = ['nombre', 'correo', 'telefono', 'direccion','edad']  # No incluir 'codigo' aquí
