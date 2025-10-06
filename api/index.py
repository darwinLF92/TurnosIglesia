import os
from django.core.wsgi import get_wsgi_application

# Configura el settings de tu proyecto Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turnos_iglesia.settings")

# Expone la aplicación WSGI que Vercel buscará
app = get_wsgi_application()
