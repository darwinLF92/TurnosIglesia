# nucleo/correos.py
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import urlencode

# Dirección desde la cual se enviarán todos los correos
FROM_NO_REPLY = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@hermandadelingeniero.com.gt")


def enviar_correo(asunto, mensaje, para):
    if not para:
        raise ValueError("Destinatario vacío al enviar correo.")

    # Siempre enviará con no-reply
    send_mail(
        asunto,
        mensaje,
        FROM_NO_REPLY,
        [para],
        fail_silently=False
    )


def enviar_confirmacion_correo(usuario, token):
    correo = getattr(usuario, "correo", None) or getattr(usuario, "email", None)
    if not correo:
        raise ValueError("El usuario no tiene correo.")

    # Construcción del enlace con parámetros
    params = urlencode({"token": token, "correo": correo})
    enlace = f"{settings.FRONTEND_URL}/auth/confirmar?{params}"

    # Debug opcional
    print("DEBUG TOKEN  :", token)
    print("DEBUG ENLACE :", enlace)

    nombre_usuario = getattr(usuario, "nombres", "") or getattr(usuario, "username", "")

    asunto = "Confirma tu cuenta - Hermandad A. El Ingeniero"
    mensaje = f"""
Hola {nombre_usuario},

Gracias por registrarte en Hermandad de la Aldea El Ingeniero, Chiquimula.

Confirma tu correo y crea tu contraseña aquí:
{enlace}

⚠️ Este correo es automático. Por favor NO responder.
"""

    enviar_correo(asunto, mensaje, correo)


def enviar_reset_password_correo(user, token):
    """
    Envía un correo con enlace para restablecer contraseña.
    """
    params = urlencode({"token": token})

    enlace = f"{settings.FRONTEND_URL}/cuentas/confirmar-password/?{params}"

    asunto = "Restablecer contraseña"
    mensaje = (
        f"Hola {user.username},\n\n"
        "Has solicitado restablecer tu contraseña.\n"
        "Haz clic en el siguiente enlace para definir una nueva contraseña:\n\n"
        f"{enlace}\n\n"
        "Si no realizaste esta solicitud, puedes ignorar este correo.\n\n"
        "⚠️ Este correo es automático. Por favor NO responder."
    )

    send_mail(
        asunto,
        mensaje,
        FROM_NO_REPLY,  # <-- SIEMPRE NO-REPLY
        [user.email],
        fail_silently=False,
    )
