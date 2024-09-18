from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
     path('crear/', views.CrearTurnoView.as_view(), name='crear_turno'),
      path('lista/', views.lista_turnos, name='lista_turnos'),
      path('editar/<int:pk>/', views.EditarTurnoView.as_view(), name='editar_turno'),
    path('eliminar/<int:pk>/', views.eliminar_turno, name='eliminar_turno'),
    path('turnos/detalle/<int:pk>/', views.detalle_turno, name='detalle_turno'),
]