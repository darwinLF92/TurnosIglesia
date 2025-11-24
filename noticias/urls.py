from django.urls import path
from . import views

app_name = 'noticias'

urlpatterns = [
    path('muro', views.muro_noticias, name='muro'),
    path('comentario/<int:post_id>/agregar/', views.agregar_comentario, name='agregar_comentario'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('likes/<int:post_id>/', views.lista_likes, name='lista_likes'),
    path('muro/comentarios/<int:post_id>/', views.lista_comentarios, name='lista_comentarios'),
     path('comentario/like/<int:comentario_id>/', views.toggle_like_comentario, name='toggle_like_comentario'),
    path('comentario/agregar/<int:post_id>/', views.agregar_comentario, name='agregar_comentario'),
     path('responder/<int:comentario_id>/', views.responder_comentario, name='responder_comentario'),
   path('noticias/eliminar/<int:post_id>/', views.eliminar_post, name='eliminar_post'),
path('noticias/editar/<int:post_id>/', views.editar_post, name='editar_post'),
path("noticias/media/<int:post_id>/", views.obtener_media_post, name="media_post"),
path("noticias/eliminar-media/<int:media_id>/", views.eliminar_media, name="eliminar_media"),
path("notificacion/<int:notif_id>/", views.leer_notificacion, name="leer_notificacion"),
path("notificaciones/historial/", views.historial_notificaciones, name="historial_notificaciones"),
path("buscar/", views.buscar_publicaciones, name="buscar_publicaciones"),






]
