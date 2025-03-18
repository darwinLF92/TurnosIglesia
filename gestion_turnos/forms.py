from django import forms
from .models import RegistroInscripcion
from procesiones.models import Procesion
from turnos.models import Turno

class InscripcionForm(forms.ModelForm):
    procesion = forms.ModelChoiceField(queryset=Procesion.objects.all(), required=True, label="Procesión")
    turno = forms.ModelChoiceField(queryset=Turno.objects.none(), required=True, label="Turno") 

    valor_turno = forms.DecimalField(max_digits=6, decimal_places=2, label="Valor del Turno", required=True)
    monto_pagado = forms.DecimalField(max_digits=6, decimal_places=2, required=True, label="Monto Pagado")
    cambio = forms.DecimalField(max_digits=6, decimal_places=2, required=False, label="Cambio")

    # ✅ Agregar widgets para mejorar la entrada de datos
    fecha_entrega_estimada = forms.DateTimeField(
        required=False, 
        label="Fecha Estimada de Entrega",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    lugar_entrega = forms.CharField(
        required=False, 
        label="Lugar de Entrega", 
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese el lugar de entrega'})
    )

    class Meta:
        model = RegistroInscripcion
        fields = ['devoto', 'procesion', 'turno', 'fecha_entrega_estimada', 'lugar_entrega', 'valor_turno', 'monto_pagado', 'cambio']

    def __init__(self, *args, **kwargs):
        super(InscripcionForm, self).__init__(*args, **kwargs)
        
        if 'procesion' in self.data:
            try:
                procesion_id = int(self.data.get('procesion'))
                self.fields['turno'].queryset = Turno.objects.filter(procesion_id=procesion_id).order_by('numero_turno')
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk:
            self.fields['turno'].queryset = self.instance.turno.procesion.turnos.order_by('numero_turno')
            self.fields['valor_turno'].initial = self.instance.valor_turno  
            self.fields['cambio'].initial = self.instance.calcular_cambio()

            # ✅ Si existe, cargar valores previos de fecha y lugar de entrega
            self.fields['fecha_entrega_estimada'].initial = self.instance.fecha_entrega_estimada
            self.fields['lugar_entrega'].initial = self.instance.lugar_entrega


# Formulario para anular inscripción
class AnularInscripcionForm(forms.ModelForm):
    class Meta:
        model = RegistroInscripcion
        fields = []  # No necesitamos campos, solo confirmación en la vista
