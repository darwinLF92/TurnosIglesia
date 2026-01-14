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
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from establecimiento.models import Establecimiento
from nucleo.correos import enviar_confirmacion_inscripcion_correo


def _obtener_o_crear_devoto_desde_usuario(user):
    """
    Devuelve un Devoto existente o crea uno si no existe.
    Prioridad de match:
    1) Si ya hay DevotoCuenta (si la usas)
    2) Por cui_o_nit (si el perfil lo tiene)
    3) Por correo (si existe)
    """
    perfil = getattr(user, "perfil", None)

    # Datos desde perfil (ajusta si tus campos cambian)
    cui = getattr(perfil, "cui", None)
    nombres = getattr(perfil, "nombres", "") or ""
    apellidos = getattr(perfil, "apellidos", "") or ""
    nombre_completo = (f"{nombres} {apellidos}").strip() or user.username

    correo = getattr(user, "email", None) or None
    telefono = getattr(perfil, "telefono", None) or ""
    direccion = getattr(perfil, "direccion", None) or ""

    # 1) Si hay CUI/NIT, buscar por ahí (porque es unique)
    if cui:
        devoto, created = Devoto.objects.get_or_create(
            cui_o_nit=cui,
            defaults={
                "nombre": nombre_completo,
                "correo": correo,
                "telefono": telefono,
                "direccion": direccion,
                "activo": True,
                "usuario_registro": user,
            }
        )
        # Si ya existía, opcionalmente sincronizas datos vacíos
        if not created:
            changed = False
            if correo and not devoto.correo:
                devoto.correo = correo; changed = True
            if telefono and not devoto.telefono:
                devoto.telefono = telefono; changed = True
            if direccion and not devoto.direccion:
                devoto.direccion = direccion; changed = True
            if nombre_completo and devoto.nombre != nombre_completo:
                devoto.nombre = nombre_completo; changed = True
            if changed:
                devoto.usuario_modificacion = user
                devoto.save(update_fields=["correo","telefono","direccion","nombre","usuario_modificacion"])
        return devoto

    # 2) Si no hay CUI, intenta por correo
    if correo:
        devoto = Devoto.objects.filter(correo=correo).first()
        if devoto:
            return devoto

    # 3) Si no hay nada para comparar, crear uno nuevo (sin cui_o_nit)
    devoto = Devoto.objects.create(
        nombre=nombre_completo,
        correo=correo,
        telefono=telefono,
        direccion=direccion,
        activo=True,
        usuario_registro=user,
    )
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

                inscripciones_devoto = RegistroInscripcion.objects.filter(
                    devoto=devoto,
                    turno__procesion=procesion,
                    inscrito=True
                ).count()

                max_turnos = procesion.turnos_devoto_online or 0

                # ⭐ Si max_turnos = 0 → ilimitado → NO se valida
                if max_turnos > 0 and inscripciones_devoto >= max_turnos:
                    messages.error(
                        request,
                        f"Estimado devoto, no puedes inscribirte a más de {max_turnos} turnos en esta procesión."
                    )
                    return redirect(
                        "inscripciones_online:inscripcion_online",
                        procesion_id=procesion.id
                    )


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
                    # 👇 NUEVO: copiar desde el Turno
                    fecha_entrega_estimada=turno_locked.fecha_entrega,
                    lugar_entrega=turno_locked.lugar_entrega,
                )

            enviar_confirmacion_inscripcion_correo(insc, usuario=request.user)

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
    devoto_cuenta = DevotoCuenta.objects.select_related("devoto").filter(user=request.user).first()

    if not devoto_cuenta:
        return render(
            request,
            "inscripciones_online/mis_inscripciones.html",
            {"sin_devoto": True}
        )

    devoto = devoto_cuenta.devoto
    query = request.GET.get("q", "").strip()

    inscripciones_qs = (
        RegistroInscripcion.objects
        .select_related("turno", "turno__procesion")
        .filter(devoto=devoto, inscrito=True)
        .order_by("-fecha_inscripcion")
    )

    if query:
        inscripciones_qs = inscripciones_qs.filter(
            Q(turno__numero_turno__icontains=query) |
            Q(turno__procesion__nombre__icontains=query)
        )

    paginator = Paginator(inscripciones_qs, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "inscripciones_online/mis_inscripciones.html",
        {
            "page_obj": page_obj,
            "query": query,
        }
    )