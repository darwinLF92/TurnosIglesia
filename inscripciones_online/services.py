import urllib.parse
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


