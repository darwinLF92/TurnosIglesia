from django.urls import path
from .views import ListaDevotosView, CrearDevotoView, EditarDevotoView, EliminarDevotoView

app_name = 'devotos'

urlpatterns = [
    path('devotos', ListaDevotosView.as_view(), name='lista_devotos'),
    path('crear/devoto/', CrearDevotoView.as_view(), name='crear_devoto'),
    path('editar/devoto/<int:pk>/', EditarDevotoView.as_view(), name='editar_devoto'),
    path('eliminar/devoto/<int:pk>/', EliminarDevotoView.as_view(), name='eliminar_devoto'),
    
]