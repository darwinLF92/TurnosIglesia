# nucleo/correos.py
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import urlencode

def enviar_correo(asunto, mensaje, para):
    if not para:
        raise ValueError("Destinatario vacío al enviar correo.")
    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [para], fail_silently=False)

def enviar_confirmacion_correo(usuario, token):
    correo = getattr(usuario, "correo", None) or getattr(usuario, "email", None)
    if not correo:
        raise ValueError("El usuario no tiene correo.")

    # ✅ Construye el enlace aquí, sólo con params
    params = urlencode({"token": token, "correo": correo})
    enlace = f"{settings.FRONTEND_URL}/auth/confirmar?{params}"

    # Debug opcional
    print("DEBUG TOKEN  :", token)
    print("DEBUG ENLACE :", enlace)

    asunto = "Confirma tu cuenta - Hermandad A. El Ingeniero"
    mensaje = f"""
Hola {getattr(usuario, "nombres", "") or getattr(usuario, "username", "")},

Gracias por registrarte en Hermandad de la Aldea El Ingeniero, Chiquimula.

Confirma tu correo y crea tu contraseña aquí:
{enlace}

Si no fuiste tú, ignora este mensaje.
"""
    enviar_correo(asunto, mensaje, correo)


def enviar_reset_password_correo(user, token):
    """
    Envía un correo con enlace para restablecer contraseña.
    El enlace apunta al mismo formulario de creación de contraseña
    que usas cuando confirman el correo, solo que por contexto el usuario
    sabrá que es para 'reset'.
    """
    params = urlencode({"token": token})

    # Si tu FRONTEND_URL es el mismo dominio del backend:
    # ejemplo: https://hermandadelingeniero.com.gt/cuentas/confirmar-password/?token=...
    enlace = f"{settings.FRONTEND_URL}/cuentas/confirmar-password/?{params}"

    asunto = "Restablecer contraseña"
    mensaje = (
        f"Hola {user.username},\n\n"
        "Has solicitado restablecer tu contraseña.\n"
        "Haz clic en el siguiente enlace para definir una nueva contraseña:\n\n"
        f"{enlace}\n\n"
        "Si no realizaste esta solicitud, puedes ignorar este correo."
    )

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )