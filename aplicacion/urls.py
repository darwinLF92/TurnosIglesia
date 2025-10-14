# aplicacion/urls.py
from django.urls import path
from . import views
from django.urls import re_path
from .views import serve_audio
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
    re_path(r'^media/(?P<filename>.+)$', serve_audio, name='serve_audio'),
        # --- Vista pública ---
    path('historia-imagenes/', views.historia_imagenes_view, name='historia_imagenes'),

# CRUD (cambia el prefijo "admin" por "panel")
    path('panel/historia-imagenes/', views.HistoriaImagenListView.as_view(),
         name='historia_imagenes_admin'),
    path('panel/historia-imagenes/crear/', views.HistoriaImagenCreateView.as_view(),
         name='historia_imagenes_crear'),
    path('panel/historia-imagenes/<int:pk>/editar/', views.HistoriaImagenUpdateView.as_view(),
         name='historia_imagenes_editar'),
    path('panel/historia-imagenes/<int:pk>/eliminar/', views.HistoriaImagenDeleteView.as_view(),
         name='historia_imagenes_eliminar'),


     # Público
    path('galeria/', views.galeria_view, name='galeria'),
    path('galeria/album/<int:pk>/', views.album_detalle_view, name='album_detalle'),

    # Panel
    path('panel/galeria/', views.AlbumListView.as_view(), name='album_admin'),
    path('panel/galeria/crear/', views.AlbumCreateView.as_view(), name='album_crear'),
    path('panel/galeria/<int:pk>/editar/', views.AlbumUpdateView.as_view(), name='album_editar'),
    path('panel/galeria/<int:pk>/eliminar/', views.AlbumDeleteView.as_view(), name='album_eliminar'),

    # Subidas
    path('panel/galeria/<int:pk>/fotos/subir/', views.album_foto_upload_view, name='album_foto_subir'),
    path('panel/galeria/<int:pk>/videos/subir/', views.album_video_upload_view, name='album_video_subir'),

      # FOTOS
    path('album/foto/<int:pk>/editar/',  views.FotoUpdateView.as_view(),  name='foto_editar'),
    path('album/foto/<int:pk>/eliminar/', views.FotoDeleteView.as_view(), name='foto_eliminar'),

    # VIDEOS
    path('album/video/<int:pk>/editar/',  views.VideoUpdateView.as_view(),  name='video_editar'),
    path('album/video/<int:pk>/eliminar/', views.VideoDeleteView.as_view(), name='video_eliminar'),


]
