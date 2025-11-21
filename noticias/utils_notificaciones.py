from .models import Notificacion

def crear_notificacion_like(usuario, post):
    if usuario == post.autor:
        return  # no notificarte a ti mismo

    Notificacion.objects.create(
        usuario=post.autor,
        tipo="like_post",
        texto=f"{usuario.get_full_name() or usuario.username} le dio Me gusta a tu publicación.",
        post=post
    )


def crear_notificacion_comentario(usuario, comentario):
    """
    Crea notificaciones tanto para comentarios en un post
    como para respuestas a comentarios.
    """

    post = comentario.post

    # 1️⃣ Notificación al dueño del post si NO es respuesta
    if comentario.padre is None and usuario != post.autor:
        Notificacion.objects.create(
            usuario=post.autor,
            tipo="comentario_post",
            texto=f"{usuario.get_full_name() or usuario.username} comentó tu publicación.",
            post=post,
            comentario=comentario
        )

    # 2️⃣ Notificación al dueño del comentario padre (respuesta)
    if comentario.padre and comentario.padre.autor != usuario:
        Notificacion.objects.create(
            usuario=comentario.padre.autor,
            tipo="respuesta_comentario",
            texto=f"{usuario.get_full_name() or usuario.username} respondió tu comentario.",
            post=post,
            comentario=comentario
        )


def crear_notificacion_like_comentario(usuario, comentario):
    """
    Crea notificación cuando alguien da 'me gusta' a un comentario.
    """
    # Evitar notificarte a ti mismo
    if usuario == comentario.autor:
        return

    Notificacion.objects.create(
        usuario=comentario.autor,
        tipo="like_comentario",
        texto=f"{usuario.get_full_name() or usuario.username} le dio Me gusta a tu comentario.",
        post=comentario.post,
        comentario=comentario
    )


# 🔴 RESPUESTA desde el modal (AJAX)
def crear_notificacion_respuesta(usuario, comentario):
    """
    Notifica cuando un usuario responde un comentario
    (usado por la vista responder_comentario AJAX).
    """

    post = comentario.post

    # Notificar al dueño del comentario padre
    if comentario.padre and comentario.padre.autor != usuario:
        Notificacion.objects.create(
            usuario=comentario.padre.autor,
            tipo="respuesta_comentario",
            texto=f"{usuario.get_full_name() or usuario.username} respondió tu comentario.",
            post=post,
            comentario=comentario
        )

    # Notificar al dueño del post si el autor no es él
    if usuario != post.autor:
        Notificacion.objects.create(
            usuario=post.autor,
            tipo="comentario_post",
            texto=f"{usuario.get_full_name() or usuario.username} respondió en tu publicación.",
            post=post,
            comentario=comentario
        )
