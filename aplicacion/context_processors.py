from establecimiento.models import Establecimiento
from django.conf import settings

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