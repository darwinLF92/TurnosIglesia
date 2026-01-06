from django.urls import path
from . import views

app_name = 'procesiones'

urlpatterns = [
    path('procesiones/', views.ListaProcesionesView.as_view(), name='lista_procesiones'),
    path('procesiones/crear/', views.CrearProcesionView.as_view(), name='crear_procesion'),
    path('procesiones/editar/<int:pk>/', views.EditarProcesionView.as_view(), name='editar_procesion'),
    path('procesiones/eliminar/<int:pk>/', views.EliminarProcesionView, name='eliminar_procesion'),
    path('ajax/reporte-turnos/', views.reporte_turnos, name='reporte_turnos'),
    path('obtener-anios/', views.obtener_anios, name='obtener_anios'),
    path('exportar-reporte-turnos-pdf/', views.exportar_reporte_turnos_pdf, name='exportar_reporte_turnos_pdf'),
    path('exportar-reporte-turnos-excel/', views.exportar_reporte_turnos_excel, name='exportar_reporte_turnos_excel'),
    path(
        'marcar-relevante/',
        views.marcar_procesion_relevante,
        name='marcar_procesion_relevante'
    ),

]

