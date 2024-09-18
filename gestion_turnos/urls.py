from django.urls import path
from . import views

app_name = 'gestion_turnos'

urlpatterns = [
    path('nueva/', views.inscribir_devoto, name='crear_inscripcion'),
    path('inscripciones', views.ListaInscripciones.as_view(), name='lista_inscripciones'),
    path('ajax/load-turnos/', views.load_turnos, name='ajax_load_turnos'),

]