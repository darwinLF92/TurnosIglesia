from django.urls import path
from .views import (
    EstablecimientoListView,
    EstablecimientoCreateView,
    EstablecimientoUpdateView,
    EstablecimientoDeleteView,
)

app_name = 'establecimiento'

urlpatterns = [
    path('establecimientos', EstablecimientoListView.as_view(), name='lista_establecimientos'),
    path('crear_nuevo/', EstablecimientoCreateView.as_view(), name='crear_establecimiento'),
    path('<int:pk>/editar/', EstablecimientoUpdateView.as_view(), name='editar_establecimiento'),
    path('<int:pk>/eliminar/', EstablecimientoDeleteView.as_view(), name='eliminar_establecimiento'),
]
