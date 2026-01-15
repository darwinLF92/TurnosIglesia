# nucleo/correos.py
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import urlencode
from django.template.loader import render_to_string
import base64
from pathlib import Path
from django.utils import timezone
from django.utils.formats import date_format
from io import BytesIO
from PIL import Image 
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from urllib.parse import urljoin

# Dirección desde la cual se enviarán todos los correos
FROM_NO_REPLY = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@hermandadelingeniero.com.gt")

import os
from pathlib import Path
from PIL import Image
from io import BytesIO
from django.conf import settings
from django.templatetags.static import static
from urllib.parse import urljoin


def make_absolute_url(path: str) -> str:
    base = getattr(settings, "FRONTEND_URL", "").rstrip("/")
    path = (path or "").lstrip("/")
    return urljoin(base + "/", path)


def cargar_imagen_procesion_url(procesion):
    """
    Genera una versión optimizada (máx 600px) de la imagen_promocional
    y devuelve una URL absoluta lista para usar en correos.
    """
    img_field = getattr(procesion, "imagen_promocional", None)

    if not img_field or not getattr(img_field, "path", None):
        # Fallback al logo estático si no hay imagen
        logo_rel = static("home/logo_hermandad.png")
        return make_absolute_url(logo_rel)

    original_path = Path(img_field.path)

    if not original_path.exists():
        logo_rel = static("home/logo_hermandad.png")
        return make_absolute_url(logo_rel)

    # Carpeta donde guardaremos las imágenes optimizadas
    optimized_dir = Path(settings.MEDIA_ROOT) / "optimizadas"
    optimized_dir.mkdir(exist_ok=True)

    # Nombre basado en el original
    optimized_path = optimized_dir / f"opt_{original_path.name}"

    # Si ya existe una optimizada previa, úsala
    if optimized_path.exists():
        return make_absolute_url(
            f"{settings.MEDIA_URL}optimizadas/opt_{original_path.name}"
        )

    # Crear nueva imagen optimizada
    try:
        with Image.open(original_path) as img:
            img = img.convert("RGB")

            max_width = 600
            if img.width > max_width:
                new_height = int(img.height * max_width / img.width)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            img.save(optimized_path, format="JPEG", quality=75, optimize=True)

        # Devolver la URL absoluta de la imagen optimizada
        return make_absolute_url(
            f"{settings.MEDIA_URL}optimizadas/opt_{original_path.name}"
        )

    except Exception:
        # Fallback si algo falla
        logo_rel = static("home/logo_hermandad.png")
        return make_absolute_url(logo_rel)


# ============================================
#  🔥 Función: cargar logo como Base64
# ============================================
def cargar_logo_base64():
    ruta_logo = Path(settings.BASE_DIR) / "staticfiles" / "home" / "logo_hermandad.png"

    if not ruta_logo.exists():
        return None

    with open(ruta_logo, "rb") as img:
        encoded = base64.b64encode(img.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    

def cargar_imagen_procesion_base64(procesion):
    """
    Devuelve la imagen_promocional optimizada (600px de ancho máx) en base64.
    Si no hay imagen, usa el logo como fallback.
    """
    img_field = getattr(procesion, "imagen_promocional", None)
    if not img_field:
        return cargar_logo_base64()

    ruta = Path(img_field.path)
    if not ruta.exists():
        return cargar_logo_base64()

    try:
        with Image.open(ruta) as img:
            # Aseguramos modo RGB para JPEG
            img = img.convert("RGB")

            max_width = 600
            if img.width > max_width:
                new_height = int(img.height * max_width / img.width)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            buffer = BytesIO()
            # calidad 75 + optimize reduce MUCHO el tamaño
            img.save(buffer, format="JPEG", quality=75, optimize=True)
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        # Por si algo falla, usamos logo normal
        return cargar_logo_base64()

    except Exception:
        # Si algo falla, regresamos al logo
        return cargar_logo_base64()


def obtener_nombre_completo(usuario):
    nombre = getattr(usuario, "first_name", "") or ""
    apellido = getattr(usuario, "last_name", "") or ""

    nombre_completo = f"{nombre} {apellido}".strip()

    return nombre_completo if nombre_completo else usuario.username



def enviar_correo_template(asunto, para, template, context):
    html_message = render_to_string(template, context)

    # Texto plano “limpio” para clientes que no soportan HTML
    texto_plano_basico = "Confirmación de inscripción.\n\n"
    texto_plano_basico += "Si no ves el contenido correctamente, abre este correo en un cliente compatible con HTML.\n\n"
    texto_plano_basico += strip_tags(html_message)[:2000]  # recortamos para no hacerlo gigante

    msg = EmailMultiAlternatives(
        subject=asunto,
        body=texto_plano_basico,
        from_email=FROM_NO_REPLY,
        to=[para],
    )
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=False)


def enviar_confirmacion_correo(usuario, token):
    correo = usuario.email

    params = urlencode({"token": token, "correo": correo})
    enlace = f"{settings.FRONTEND_URL}/auth/confirmar?{params}"

    context = {
        "titulo_correo": "Registro de datos",
        "nombre_completo": obtener_nombre_completo(usuario),
        "enlace": enlace,
        "logo_base64": cargar_logo_base64(),
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
        "logo_base64": cargar_logo_base64(),
    }

    enviar_correo_template(
        "Restablecer contraseña",
        user.email,
        "nucleo/reset_password.html",
        context
    )


def enviar_confirmacion_inscripcion_correo(insc, usuario=None):
    """
    Envía correo de confirmación al devoto/usuario con datos de inscripción.

    - insc: RegistroInscripcion
    - usuario: request.user (opcional, para tomar email/nombre)
    """

    # 1) Determinar correo destino (prioridad: user.email -> devoto.correo)
    correo = None
    if usuario and getattr(usuario, "email", None):
        correo = usuario.email

    # Si tu modelo Devoto tiene correo:
    if not correo and getattr(insc.devoto, "correo", None):
        correo = insc.devoto.correo

    if not correo:
        # No hay a quién enviar
        return False

    turno = insc.turno
    procesion = turno.procesion

    # 2) Fechas bonitas (si hay fecha_entrega)
    fecha_entrega_txt = "Pendiente"
    dt_entrega = getattr(turno, "fecha_entrega", None)

    if dt_entrega:
        # ✅ Asegurar que sea "aware" antes de localtime()
        if timezone.is_naive(dt_entrega):
            dt_entrega = timezone.make_aware(dt_entrega, timezone.get_current_timezone())

        fecha_entrega_txt = date_format(
            timezone.localtime(dt_entrega),
            "d/m/Y h:i A"
        )

    lugar_entrega_txt = getattr(turno, "lugar_entrega", None) or "Pendiente"

    # 3) Nombre para el saludo
    nombre = None
    if usuario:
        nombre = obtener_nombre_completo(usuario)
    if not nombre:
        # fallback
        nombre = getattr(insc.devoto, "nombre", None) or "Devoto"

    # 4) Contexto para el template
    context = {
        "titulo_correo": "Confirmación de inscripción",
        "nombre_completo": nombre,
        "banner_url": cargar_imagen_procesion_url(procesion),
        "clase_turno": turno.clase_turno,
        "turno_numero": turno.numero_turno,
        "procesion_nombre": procesion.nombre,
        "Procesión_descripcion": procesion.descripcion,
        "fecha_entrega": fecha_entrega_txt,
        "lugar_entrega": lugar_entrega_txt,
        "codigo_inscripcion": insc.codigo,
        "marcha_funebre": turno.marcha_funebre,
        "referencia_turno": turno.referencia,
        "fecha_procesion": procesion.fecha,
    }

    enviar_correo_template(
        "Confirmación de inscripción - Hermandad Aldea El Ingeniero",
        correo,
        "nucleo/confirmacion_inscripcion.html",
        context
    )
    return True