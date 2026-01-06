from django import forms
from .models import RegistroInscripcion
from procesiones.models import Procesion
from turnos.models import Turno
from django.core.exceptions import ValidationError

from django import forms
from django.core.exceptions import ValidationError
from turnos.models import Turno
from procesiones.models import Procesion
from gestion_turnos.models import RegistroInscripcion


class InscripcionForm(forms.ModelForm):

    procesion = forms.ModelChoiceField(
        queryset=Procesion.objects.filter(activo=True),
        required=True,
        label="Procesión"
    )

    turno = forms.ModelChoiceField(
        queryset=Turno.objects.none(),
        required=True,
        label="Turno"
    )

    valor_turno = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        label="Valor del Turno",
        required=True
    )

    monto_pagado = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=True,
        label="Monto Pagado"
    )

    cambio = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        label="Cambio"
    )

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
        fields = [
            'devoto',
            'procesion',
            'turno',
            'fecha_entrega_estimada',
            'lugar_entrega',
            'valor_turno',
            'monto_pagado',
            'cambio'
        ]

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # 👈 IMPORTANTE
        super().__init__(*args, **kwargs)

        self.turnos_reservados = []

        es_admin = (
            self.user and
            self.user.groups.filter(name="Administrador").exists()
        )

        # 🔹 Cargar turnos según procesión
        if 'procesion' in self.data:
            try:
                procesion_id = int(self.data.get('procesion'))
                qs = Turno.objects.filter(
                    procesion_id=procesion_id,
                    activo=True
                ).order_by('numero_turno')
            except (ValueError, TypeError):
                qs = Turno.objects.none()

        elif self.instance.pk:
            qs = Turno.objects.filter(
                procesion=self.instance.turno.procesion,
                activo=True
            ).order_by('numero_turno')
        else:
            qs = Turno.objects.none()

        self.fields['turno'].queryset = qs

        # 🔹 Texto del select
        self.fields['turno'].label_from_instance = (
            lambda t: (
                f"Turno {t.numero_turno} - "
                f"{t.referencia or 'Sin referencia'} - "
                f"Q{t.valor}"
                f"{' (Reservado)' if t.reservado_hermandad else ''}"
            )
        )

        # 🔹 Marcar turnos reservados (solo para frontend)
        if not es_admin:
            self.turnos_reservados = [
                str(t.id) for t in qs if t.reservado_hermandad
            ]

        # 🔹 Valores iniciales al editar
        if self.instance.pk:
            self.fields['valor_turno'].initial = self.instance.valor_turno
            self.fields['cambio'].initial = self.instance.calcular_cambio()
            self.fields['fecha_entrega_estimada'].initial = self.instance.fecha_entrega_estimada
            self.fields['lugar_entrega'].initial = self.instance.lugar_entrega

    # ------------------------------------------------------------------
    # VALIDACIONES
    # ------------------------------------------------------------------
    def clean(self):
        cleaned_data = super().clean()
        devoto = cleaned_data.get("devoto")
        turno = cleaned_data.get("turno")

        if not turno:
            return cleaned_data

        # 🔒 Turno reservado → solo admin
        if turno.reservado_hermandad:
            es_admin = (
                self.user and
                self.user.groups.filter(name="Administrador").exists()
            )
            if not es_admin:
                raise ValidationError(
                    "Este turno está reservado exclusivamente para hermandades."
                )

        # 🔁 Evitar doble inscripción
        if devoto:
            existe = RegistroInscripcion.objects.filter(
                devoto=devoto,
                turno=turno,
                inscrito=True
            )
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)

            if existe.exists():
                raise ValidationError(
                    "Este devoto ya está inscrito en el turno seleccionado."
                )

        # 🚦 Validar capacidad
        inscripciones_actuales = RegistroInscripcion.objects.filter(
            turno=turno,
            inscrito=True
        ).count()

        if inscripciones_actuales >= turno.capacidad:
            raise ValidationError(
                "El turno seleccionado ya se encuentra completo."
            )

        return cleaned_data


# Formulario para anular inscripción
class AnularInscripcionForm(forms.ModelForm):
    class Meta:
        model = RegistroInscripcion
        fields = []  # No necesitamos campos, solo confirmación en la vista
