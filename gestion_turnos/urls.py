from django.urls import path
from . import views

app_name = 'gestion_turnos'

urlpatterns = [
    path('nueva/', views.inscribir_devoto, name='crear_inscripcion'),
    path('inscripciones', views.ListaInscripciones.as_view(), name='lista_inscripciones'),
    path('ajax/load-turnos/', views.load_turnos, name='load_turnos'),
    path('obtener_precio_turno/', views.obtener_precio_turno, name='obtener_precio_turno'),
    path('ajax/devotos-activos/', views.ajax_devotos_activos, name='ajax_devotos_activos'),
    path('ajax/procesiones-activas/', views.ajax_procesiones_activas, name='ajax_procesiones_activas'),
    path('inscripcion/<int:inscripcion_id>/anular/', views.AnularInscripcionView.as_view(), name='anular_inscripcion'),
    path('inscripcion/<int:inscripcion_id>/comprobante/', views.ComprobanteInscripcionView.as_view(), name='comprobante_inscripcion'),
    path('inscripcion/<int:inscripcion_id>/detalle/', views.DetalleInscripcionView.as_view(), name='detalle_inscripcion'),
    path('inscripcion/<int:inscripcion_id>/comprobantepdf/', views.ComprobanteInscripcionPDFView.as_view(), name='comprobante_inscripcion_pdf'),
    path('inscripcion/<int:inscripcion_id>/enviar-comprobante/', views.EnviarComprobanteWhatsAppView.as_view(), name='enviar_comprobante_whatsapp'),
    path("entrega_turnos/", views.ListaEntregaTurnos.as_view(), name="lista_entrega_turnos"),
    path("entregar_turno/<int:inscripcion_id>/", views.EntregarTurnoView.as_view(), name="entregar_turno"),
    path("gestion_turnos/validar_entrega/<int:inscripcion_id>/", views.ValidarEntregaTurnoView.as_view(), name="validar_entrega"),
    path('gestion_turnos/<int:inscripcion_id>/recepcion/', views.ComprobanteRecepcionView.as_view(), name='comprobante_recepcion'),
    path('recepcion/<int:inscripcion_id>/recepcionpdf/', views.ComprobanteRecepcionPDFView.as_view(), name='comprobante_recepcion_pdf'),

]