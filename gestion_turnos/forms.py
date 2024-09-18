from django import forms
from .models import RegistroInscripcion, Turno
from devotos.models import Devoto  # Importa Devoto desde el lugar correcto
from procesiones.models import Procesion

class InscripcionForm(forms.ModelForm):
    procesion = forms.ModelChoiceField(queryset=Procesion.objects.all(), required=True, label="Procesión")
    turno = forms.ModelChoiceField(queryset=Turno.objects.none(), required=True, label="Turno")  # Inicialmente vacío

    class Meta:
        model = RegistroInscripcion
        fields = ['devoto', 'procesion', 'turno']

    def __init__(self, *args, **kwargs):
        super(InscripcionForm, self).__init__(*args, **kwargs)
        if 'procesion' in self.data:
            try:
                procesion_id = int(self.data.get('procesion'))
                self.fields['turno'].queryset = Turno.objects.filter(procesion_id=procesion_id).order_by('numero_turno')
            except (ValueError, TypeError):
                pass  # Formulario inválido o datos iniciales; no hagas nada
        elif self.instance.pk:
            self.fields['turno'].queryset = self.instance.turno.procesion.turnos.order_by('numero_turno')

    def clean_turno(self):
        turno = self.cleaned_data.get('turno')
        if turno and turno.inscripciones.filter(inscrito=True).count() >= turno.capacidad:
            raise forms.ValidationError("Este turno ya está completo.")
        return turno
