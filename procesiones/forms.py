from django import forms
from .models import Procesion

class ProcesionForm(forms.ModelForm):
    class Meta:
        model = Procesion
        fields = [
            'nombre',
            'descripcion',
            'fecha',
            'es_relevante',
            'turnos_devoto_online',
            'turnos_devoto_local',
            'imagen_promocional',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'turnos_devoto_online': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'turnos_devoto_local': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'es_relevante': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'imagen_promocional': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
