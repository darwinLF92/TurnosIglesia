from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.template.loader import render_to_string
from procesiones.models import Procesion
from turnos.models import Turno
from devotos.models import Devoto
from gestion_turnos.models import RegistroInscripcion  # ajusta el import según tu app real
from weasyprint import HTML
from .forms import InscripcionOnlineForm
from .models import DevotoCuenta, TurnoAcceso
from .services import generar_url_whatsapp
from .services import enviar_whatsapp_confirmacion
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from establecimiento.models import Establecimiento


def _obtener_o_crear_devoto_desde_usuario(user) -> Devoto:
    """
    Crea o reutiliza Devoto a partir del UserProfile si existe.
    Usa DevotoCuenta para mapear user -> devoto.
    """
    if hasattr(user, "devoto_cuenta"):
        return user.devoto_cuenta.devoto

    perfil = getattr(user, "perfil", None)
    nombre = (f"{perfil.nombres or ''} {perfil.apellidos or ''}".strip() if perfil else user.get_username())
    telefono = (perfil.telefono if perfil and perfil.telefono else "")

    # Puedes decidir reglas: por CUI si existe, o por correo, etc.
    cui = (perfil.cui if perfil else None)
    correo = user.email or (perfil.user.email if perfil else None)

    devoto = Devoto.objects.create(
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        direccion=(perfil.direccion if perfil and perfil.direccion else ""),
        cui_o_nit=cui,  # si tu CUI coincide con este campo
        fecha_nacimiento=(perfil.fecha_nacimiento if perfil else None),
        activo=True,
        usuario_registro=user
    )
    DevotoCuenta.objects.create(user=user, devoto=devoto)
    return devoto



@login_required
def inscripcion_online(request, procesion_id):
    procesion = get_object_or_404(Procesion, id=procesion_id)

    # 🔹 Turnos visibles SOLO para inscripción en línea
    turnos = Turno.objects.filter(
        procesion=procesion,
        activo=True,
        reservado_hermandad=False
    )

    if request.method == "POST":
        form = InscripcionOnlineForm(request.POST, procesion=procesion)
        confirmado = request.POST.get("confirmado") == "1"

        if form.is_valid():
            turno = form.cleaned_data["turno"]

            # 1️⃣ PASO DE CONFIRMACIÓN (SIN GUARDAR)
            if not confirmado:
                return render(
                    request,
                    "inscripciones_online/inscripcion_online.html",
                    {
                        "procesion": procesion,
                        "turnos": turnos,
                        "form": form,
                        "resumen": {
                            "procesion": procesion.nombre,
                            "fecha": procesion.fecha,
                            "turno": f"Turno {turno.numero_turno}",
                            "valor": turno.valor,
                        },
                    },
                )

            # 2️⃣ GUARDADO DEFINITIVO (CON BLOQUEO)
            with transaction.atomic():
                turno_locked = (
                    Turno.objects
                    .select_for_update()
                    .get(id=turno.id)
                )

                # ❌ BLOQUEAR TURNOS RESERVADOS (SEGURIDAD BACKEND)
                if turno_locked.reservado_hermandad:
                    messages.error(
                        request,
                        "Este turno está reservado y no permite inscripciones en línea."
                    )
                    return redirect(
                        "inscripciones_online:inscripcion_online",
                        procesion_id=procesion.id
                    )

                inscritos = RegistroInscripcion.objects.filter(
                    turno=turno_locked,
                    inscrito=True
                ).count()

                # ❌ SIN CUPO
                if inscritos >= turno_locked.capacidad:
                    messages.error(
                        request,
                        "Este turno ya no tiene cupo disponible."
                    )
                    return redirect(
                        "inscripciones_online:inscripcion_online",
                        procesion_id=procesion.id
                    )

                devoto = _obtener_o_crear_devoto_desde_usuario(request.user)

                # ❌ EVITAR DOBLE INSCRIPCIÓN
                if RegistroInscripcion.objects.filter(
                    devoto=devoto,
                    turno=turno_locked,
                    inscrito=True
                ).exists():
                    messages.warning(
                        request,
                        "Ya estás inscrito en este turno."
                    )
                    return redirect(
                        "inscripciones_online:inscripcion_online",
                        procesion_id=procesion.id
                    )

                # ✅ CREAR INSCRIPCIÓN
                insc = RegistroInscripcion.objects.create(
                    devoto=devoto,
                    turno=turno_locked,
                    fecha_inscripcion=timezone.now(),
                    inscrito=True,
                    valor_turno=turno_locked.valor,
                    monto_pagado=0,
                    tipo_inscripcion="online",
                )

            # ✅ ÉXITO
            return redirect(
                "inscripciones_online:inscripcion_online_exito",
                codigo=insc.codigo
            )

    else:
        form = InscripcionOnlineForm(procesion=procesion)

    return render(
        request,
        "inscripciones_online/inscripcion_online.html",
        {
            "procesion": procesion,
            "turnos": turnos,
            "form": form,
        },
    )

@login_required
def inscripcion_online_exito(request, codigo):
    insc = get_object_or_404(RegistroInscripcion, codigo=codigo)
    return render(request, "inscripciones_online/exito.html", {"insc": insc})


@login_required
def comprobante_inscripcion_imagen(request, codigo):
    insc = get_object_or_404(RegistroInscripcion, codigo=codigo)

    establecimiento = Establecimiento.objects.filter(estado='activo').first()

    return render(
        request,
        "inscripciones_online/comprobante_imagen.html",
        {
            "insc": insc,
            "establecimiento": establecimiento,
        }
    )


@login_required
def mis_inscripciones(request):
    try:
        devoto = request.user.devoto_cuenta.devoto
    except DevotoCuenta.DoesNotExist:
        return render(request, "inscripciones_online/mis_inscripciones.html", {
            "sin_devoto": True
        })

    query = request.GET.get("q", "").strip()

    inscripciones_qs = (
        RegistroInscripcion.objects
        .select_related("turno", "turno__procesion")
        .filter(devoto=devoto, inscrito=True)
    )

    # 🔍 BÚSQUEDA
    if query:
        inscripciones_qs = inscripciones_qs.filter(
            Q(turno__numero_turno__icontains=query) |
            Q(turno__procesion__nombre__icontains=query)
        )

    inscripciones_qs = inscripciones_qs.order_by("-fecha_inscripcion")

    # 📄 PAGINACIÓN
    paginator = Paginator(inscripciones_qs, 8)  # 8 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "inscripciones_online/mis_inscripciones.html", {
        "page_obj": page_obj,
        "query": query,
    })