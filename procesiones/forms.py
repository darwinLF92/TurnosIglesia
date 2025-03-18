from django import forms
from .models import Procesion

class ProcesionForm(forms.ModelForm):
    class Meta:
        model = Procesion
        fields = ['nombre', 'descripcion', 'fecha']
        widgets = {
            'fecha': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date', 'class': 'form-control'}),
        }