from django import forms
from .models import Turno

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['procesion', 'numero_turno', 'referencia', 'marcha_funebre', 'capacidad', 'valor']
        widgets = {
            'procesion': forms.Select(attrs={'class': 'form-control'}),
            'numero_turno': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        procesion = cleaned_data.get('procesion')
        numero_turno = cleaned_data.get('numero_turno')

        if procesion and numero_turno:
            if Turno.objects.filter(procesion=procesion, numero_turno=numero_turno).exists():
                self.add_error('numero_turno', f"Ya existe un turno número {numero_turno} para esta procesión.")
        
        return cleaned_data
