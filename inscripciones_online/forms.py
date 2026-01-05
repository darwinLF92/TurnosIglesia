from django import forms
from turnos.models import Turno

class InscripcionOnlineForm(forms.Form):
    turno = forms.ModelChoiceField(
        queryset=Turno.objects.none(),
        empty_label="Seleccione un turno",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        procesion = kwargs.pop('procesion', None)
        super().__init__(*args, **kwargs)

        self.turnos_reservados = []  # 👈 IDs a deshabilitar

        if procesion:
            qs = (
                Turno.objects
                .filter(procesion=procesion, activo=True)
                .order_by('numero_turno')
            )

            self.fields['turno'].queryset = qs

            # Texto del select
            self.fields['turno'].label_from_instance = (
                lambda turno: (
                    f"Turno {turno.numero_turno} - "
                    f"{turno.referencia or 'Sin referencia'} - "
                    f"Q{turno.valor} - "
                    f"{turno.tipo_turno}"
                    f"{' (Reservado Hermandades)' if turno.reservado_hermandad else ''}"
                )
            )

            # Guardar IDs de turnos reservados
            self.turnos_reservados = [
                str(turno.id) for turno in qs if turno.reservado_hermandad
            ]
