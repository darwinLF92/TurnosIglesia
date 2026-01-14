from django import template
from django.utils.timesince import timesince as dj_timesince
from django.utils import timezone

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name: str) -> bool:
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists() or user.is_superuser

@register.filter
def timesince_es(value):
    """
    Devuelve una cadena tipo:
    - 'unos segundos'
    - '5 minutos'
    - '3 horas'
    - '2 días'
    - '4 semanas'
    - '3 meses'
    - '2 años'
    en español, según el tiempo transcurrido desde 'value' hasta ahora.
    """
    if not value:
        return ""

    # 🔹 Normalizar ambos datetimes a "naive" en hora local
    now = timezone.now()

    # Si tienen tz, los pasamos a hora local y les quitamos tzinfo
    if timezone.is_aware(now):
        now = timezone.localtime(now).replace(tzinfo=None)

    if timezone.is_aware(value):
        value = timezone.localtime(value).replace(tzinfo=None)

    # Si value es naive y now también, no pasa nada.
    # Si value es naive y now era aware, ya convertimos now a naive arriba.

    delta = now - value
    seconds = int(delta.total_seconds())

    if seconds < 60:
        return "unos segundos"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minuto{'s' if minutes != 1 else ''}"

    hours = minutes // 60
    if hours < 24:
        return f"{hours} hora{'s' if hours != 1 else ''}"

    days = hours // 24
    if days < 7:
        return f"{days} día{'s' if days != 1 else ''}"

    weeks = days // 7
    if weeks < 4:
        return f"{weeks} semana{'s' if weeks != 1 else ''}"

    months = days // 30
    if months < 12:
        return f"{months} mes{'es' if months != 1 else ''}"

    years = days // 365
    return f"{years} año{'s' if years != 1 else ''}"
