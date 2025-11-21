from establecimiento.models import Establecimiento
from django.conf import settings
from noticias.models import Notificacion

def logo_establecimiento(request):
    logo_url = None
    nombre = None
    try:
        # primero uno activo; si no hay, el más reciente
        est = (Establecimiento.objects.filter(estado='activo').first()
               or Establecimiento.objects.order_by('-id').first())
        if est:
            nombre = est.nombre or est.nombre_hermandad
            if getattr(est, 'logo', None):
                # asegura que exista archivo
                if getattr(est.logo, 'name', ''):
                    logo_url = est.logo.url
    except Exception:
        pass
    return {"logo_url": logo_url, "establecimiento_nombre": nombre}


def system_meta(request):
    # devuelve el diccionario tal cual a los templates
    return {"system_meta": settings.SYSTEM_META}


def notificaciones_context(request):
    if not request.user.is_authenticated:
        return {}

    notif_no_leidas = Notificacion.objects.filter(
        usuario=request.user, leido=False
    ).order_by("-creado_en")

    notif_leidas = Notificacion.objects.filter(
        usuario=request.user, leido=True
    ).order_by("-creado_en")[:10]

    # historial de las últimas 5 (sin importar si están leídas o no)
    historial = Notificacion.objects.filter(
        usuario=request.user
    ).order_by("-creado_en")[:5]

    return {
        "notif_no_leidas": notif_no_leidas,
        "notif_leidas": notif_leidas,
        "notif_total_no_leidas": notif_no_leidas.count(),
        "notif_historial": historial,
    }
