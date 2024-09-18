from django import forms
from .models import Turno

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['procesion', 'numero_turno','referencia','marcha_funebre', 'capacidad', 'valor']
        widgets = {
            'procesion': forms.Select(attrs={'class': 'form-control'}),
            'numero_turno': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }