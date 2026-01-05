import urllib.parse
from twilio.rest import Client
from django.conf import settings

def generar_url_whatsapp(inscripcion, request):
    telefono = inscripcion.devoto.telefono

    if not telefono:
        return None

    # Limpiar número (solo dígitos)
    telefono = ''.join(filter(str.isdigit, telefono))

    nombre_procesion = inscripcion.turno.procesion.nombre
    numero_turno = inscripcion.turno.numero_turno
    marcha_funebre = inscripcion.turno.marcha_funebre or ""
    referencia = inscripcion.turno.referencia or ""
    fecha_procesion = inscripcion.turno.procesion.fecha.strftime("%d-%m-%Y")

    fecha_entrega = (
        inscripcion.fecha_entrega_estimada.strftime("%d-%m-%Y")
        if inscripcion.fecha_entrega_estimada else "No definida"
    )
    hora_entrega = (
        inscripcion.fecha_entrega_estimada.strftime("%H:%M")
        if inscripcion.fecha_entrega_estimada else ""
    )
    lugar_entrega = inscripcion.lugar_entrega or "No definido"

    mensaje = (
        f"Hola {inscripcion.devoto.nombre},\n\n"
        f"✅ Inscripción confirmada\n\n"
        f"Procesión: *{nombre_procesion}*\n"
        f"Fecha: *{fecha_procesion}*\n"
        f"Turno: *{numero_turno}* - *{referencia}*\n\n"
        f"🎶 Marcha Fúnebre: {marcha_funebre}\n"
        f"📅 Entrega: {fecha_entrega} {hora_entrega}\n"
        f"🔐 Contraseña del Turno: *{inscripcion.codigo}*\n"
        f"📍 Lugar: {lugar_entrega}\n\n"
        f"🙏 Que tenga un bendecido turno."
    )

    mensaje_codificado = urllib.parse.quote(mensaje)

    return f"https://wa.me/{telefono}?text={mensaje_codificado}"


def enviar_whatsapp_confirmacion(inscripcion):
    if not inscripcion.devoto.telefono:
        return

    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    mensaje = (
        "🙏 *Inscripción confirmada*\n\n"
        f"Código: {inscripcion.codigo}\n"
        f"Procesión: {inscripcion.turno.procesion.nombre}\n"
        f"Turno: {inscripcion.turno.numero_turno}\n"
        f"Fecha: {inscripcion.turno.procesion.fecha.strftime('%d/%m/%Y')}\n\n"
        "Gracias por formar parte 🙌"
    )

    client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=f"whatsapp:{inscripcion.devoto.telefono}",
        body=mensaje
    )