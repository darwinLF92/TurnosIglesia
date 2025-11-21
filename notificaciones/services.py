import os
from django.utils import timezone

def notificar_cita_whatsapp(cita):
    txt = (
        f"Reserva confirmada:\n"
        f"Barbero: {cita.barbero.nombre_mostrado}\n"
        f"Servicio: {cita.servicio.nombre}\n"
        f"Fecha/Hora: {cita.fecha_hora_inicio.astimezone(timezone.get_current_timezone()).strftime('%d-%m-%Y %H:%M')}\n"
        f"Cliente: {cita.cliente.get_full_name() or cita.cliente.username}"
    )
    tel_barberia = os.getenv("TELEFONO_BARBERIA_E164","+50200000000")
    tel_cliente = getattr(cita.cliente, "telefono", "")

    if os.getenv("TWILIO_CUENTA_SID"):
        from .providers.twilio_whatsapp import enviar_whatsapp_twilio
        if tel_cliente: enviar_whatsapp_twilio(tel_cliente, txt)
        if tel_barberia: enviar_whatsapp_twilio(tel_barberia, "Nueva cita:\n"+txt)
    else:
        from .providers.enlace_whatsapp import enlace_click_to_chat
        enlaces = {}
        if tel_cliente:
            enlaces["cliente"] = enlace_click_to_chat(tel_cliente, txt)
        if tel_barberia:
            enlaces["barberia"] = enlace_click_to_chat(tel_barberia, "Nueva cita:\n"+txt)
        return enlaces
