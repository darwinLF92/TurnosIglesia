from django import forms
from .models import Turno

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = [
            'procesion',
            'numero_turno',
            'referencia',
            'marcha_funebre',
            'capacidad',
            'valor',
            'tipo_turno',
            'clase_turno',
            'fecha_entrega',      
            'lugar_entrega',     
            'reservado_hermandad',
            'nombre_hermandad_visitante',
        ]

        widgets = {
            'procesion': forms.Select(attrs={'class': 'form-control'}),
            'numero_turno': forms.NumberInput(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'marcha_funebre': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            # ✅ SELECT para tipo de turno
            'tipo_turno': forms.Select(attrs={
                'class': 'form-control'
            }),
            'clase_turno': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reservado_hermandad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nombre_hermandad_visitante': forms.TextInput(attrs={'class': 'form-control'}),

            # 👉 widgets nuevos
            'fecha_entrega': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'lugar_entrega': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        procesion = cleaned_data.get('procesion')
        numero_turno = cleaned_data.get('numero_turno')

        reservado = cleaned_data.get("reservado_hermandad")
        nombre = (cleaned_data.get("nombre_hermandad_visitante") or "").strip()

        # 1) Validar turno único por procesión
        if procesion and numero_turno:
            qs = Turno.objects.filter(procesion=procesion, numero_turno=numero_turno)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('numero_turno', f"Ya existe un turno número {numero_turno} para esta procesión.")

        # 2) Regla: nombre de hermandad visitante es OPCIONAL
        # - Si no está reservado → no tiene sentido guardar nombre
        if not reservado:
            cleaned_data["nombre_hermandad_visitante"] = None
        else:
            # Si está reservado y el nombre viene vacío, lo guardamos como None (permitido)
            cleaned_data["nombre_hermandad_visitante"] = nombre or None

        return cleaned_data
