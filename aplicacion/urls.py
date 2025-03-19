# aplicacion/urls.py
from django.urls import path
from . import views
from .views import (
    InformacionListView, InformacionCreateView, InformacionUpdateView, InformacionDeleteView,
    ConfiguracionHomeListView,
    ConfiguracionHomeCreateView,
    ConfiguracionHomeUpdateView,
    ConfiguracionHomeDeleteView,
    ImagenPresentacionCreateView,
    ImagenPresentacionListView,
    ImagenPresentacionUpdateView,
    ImagenPresentacionDeleteView,
    # Agrega aquí las vistas de las demás secciones
)

app_name = 'aplicacion'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
     path('informacion/', InformacionListView.as_view(), name='informacion_list'),
    path('informacion/crear/', InformacionCreateView.as_view(), name='informacion_create'),
    path('informacion/editar/<int:pk>/', InformacionUpdateView.as_view(), name='informacion_edit'),
    path('informacion/eliminar/<int:pk>/', InformacionDeleteView.as_view(), name='informacion_delete'),
    path('configuraciones/', ConfiguracionHomeListView.as_view(), name='configuracion_home_list'),
    path('configuraciones/crear/', ConfiguracionHomeCreateView.as_view(), name='configuracion_home_create'),
    path('configuraciones/editar/<int:pk>/', ConfiguracionHomeUpdateView.as_view(), name='configuracion_home_edit'),
    path('configuraciones/eliminar/<int:pk>/', ConfiguracionHomeDeleteView.as_view(), name='configuracion_home_delete'),
    path('quienes-somos/', views.quienes_somos_view, name='quienes_somos'),
    path('informacion/new/', views.crear_informacion, name='crear_informacion'),
     path('informacion/listar/', InformacionListView.as_view(), name='informacion_listar'),
   path('informacion/update/<int:pk>/', views.editar_informacion, name='editar_informacion'),

    path('informacion/delete/<int:pk>/', InformacionDeleteView.as_view(), name='eliminar_informacion'),
    path('imagen/eliminar/<int:pk>/', views.eliminar_imagen, name='eliminar_imagen'),
    path('presentacion/crear/', ImagenPresentacionCreateView.as_view(), name='imagen_presentacion_create'),
    path('presentacion/', ImagenPresentacionListView.as_view(), name='imagen_presentacion_list'),
    path('presentacion/editar/<int:pk>/', ImagenPresentacionUpdateView.as_view(), name='imagen_presentacion_edit'),
    path('presentacion/eliminar/<int:pk>/', ImagenPresentacionDeleteView.as_view(), name='imagen_presentacion_delete'),

    path('marchas/', views.lista_marchas, name='lista_marchas'),
    path('marchas/subir/', views.subir_marcha, name='subir_marcha'),
     path('marchas/favorito/<int:marcha_id>/', views.aumentar_favorito, name='aumentar_favorito'),
     # urls.py
    path('marchas/favorito/toggle/<int:marcha_id>/', views.toggle_favorito, name='toggle_favorito'),
    path('marchas/es-favorita/<int:marcha_id>/', views.es_favorita, name='es_favorita'),
    path('marchas/<int:marcha_id>/editar/', views.editar_marcha, name='editar_marcha'),
    path('marchas/<int:marcha_id>/eliminar/', views.eliminar_marcha, name='eliminar_marcha'),




]
