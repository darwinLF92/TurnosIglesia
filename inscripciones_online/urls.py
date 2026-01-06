from django.urls import path
from . import views

app_name = 'inscripciones_online'

urlpatterns = [
    path("procesion/<int:procesion_id>/", views.inscripcion_online, name="inscripcion_online"),
    path("exito/<str:codigo>/", views.inscripcion_online_exito, name="inscripcion_online_exito"),
    path(
    "comprobante/<str:codigo>/imagen/",
    views.comprobante_inscripcion_imagen,
    name="comprobante_imagen"
    ),

    path(
    "mis-inscripciones/",
    views.mis_inscripciones,
    name="mis_inscripciones"
    ),

]
