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

        self.turnos_reservados = []  # IDs a deshabilitar

        if procesion:
            qs = (
                Turno.objects
                .filter(procesion=procesion, activo=True)
                .order_by('numero_turno')
            )
            self.fields['turno'].queryset = qs

            # ✅ Texto del select usando tu lógica del modelo
            def label(turno: Turno) -> str:
                ref = turno.referencia or "Sin referencia"
                tipo = turno.get_tipo_turno_display()  # Caballeros/Damas/Infantil/Sin especificar

                # Parte base que tú ya estabas mostrando
                base = f"Turno {turno.numero_turno} - {ref} - Q{turno.valor} - {tipo}"

                # ✅ Reglas de reservado
                if turno.reservado_con_nombre():
                    return f"{base} - Reservado (Hermandades Invitadas)"

                if turno.reservado_sin_nombre():
                    return f"{base} - Reservado (Extraordinario)"

                # No reservado: muestra Ordinario/Extraordinario según clase_turno
                return f"{base} - ({turno.get_clase_turno_display()})"

            self.fields['turno'].label_from_instance = label

            # ✅ IDs reservados (si quieres deshabilitar TODOS los reservados)
            self.turnos_reservados = [str(t.id) for t in qs if t.reservado_hermandad]
