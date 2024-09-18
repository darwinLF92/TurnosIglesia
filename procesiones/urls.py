from django.urls import path
from . import views

app_name = 'procesiones'

urlpatterns = [
    path('procesiones/', views.ListaProcesionesView.as_view(), name='lista_procesiones'),
    path('procesiones/crear/', views.CrearProcesionView.as_view(), name='crear_procesion'),
    path('procesiones/editar/<int:pk>/', views.EditarProcesionView.as_view(), name='editar_procesion'),
    path('procesiones/eliminar/<int:pk>/', views.EliminarProcesionView, name='eliminar_procesion'),
]
