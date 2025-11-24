# nucleo/correos.py
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import urlencode
from django.template.loader import render_to_string
# Dirección desde la cual se enviarán todos los correos
FROM_NO_REPLY = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@hermandadelingeniero.com.gt")

def obtener_nombre_completo(usuario):
    nombre = getattr(usuario, "first_name", "") or ""
    apellido = getattr(usuario, "last_name", "") or ""

    nombre_completo = f"{nombre} {apellido}".strip()

    return nombre_completo if nombre_completo else usuario.username



def enviar_correo_template(asunto, para, template, context):
    html_message = render_to_string(template, context)
    mensaje_texto = f"Por favor abre este correo usando un cliente compatible con HTML.\n\nEnlace: {context.get('enlace','')}"
    
    send_mail(
        asunto,
        mensaje_texto,
        FROM_NO_REPLY,
        [para],
        html_message=html_message,
        fail_silently=False,
    )


def enviar_confirmacion_correo(usuario, token):
    correo = usuario.email

    params = urlencode({"token": token, "correo": correo})
    enlace = f"{settings.FRONTEND_URL}/auth/confirmar?{params}"

    context = {
        "titulo_correo": "Registro de datos",
        "nombre_completo": obtener_nombre_completo(usuario),
        "enlace": enlace,
        "logo_url": f"{settings.FRONTEND_URL}/static/img/logo.png",
    }

    enviar_correo_template(
        "Validación de registro - Hermandad Aldea El Ingeniero",
        correo,
        "nucleo/confirmacion.html",
        context
    )



def enviar_reset_password_correo(user, token):
    params = urlencode({"token": token})
    enlace = f"{settings.FRONTEND_URL}/cuentas/confirmar-password/?{params}"

    context = {
        "titulo_correo": "Restablecer contraseña",
        "nombre_completo": obtener_nombre_completo(user),
        "enlace": enlace,
        "logo_url": f"{settings.FRONTEND_URL}/static/img/logo.png",
    }

    enviar_correo_template(
        "Restablecer contraseña",
        user.email,
        "nucleo/reset_password.html",
        context
    )


