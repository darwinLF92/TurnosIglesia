from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils.timesince import timesince
from .forms import PostForm, ComentarioForm
from .models import Notificacion, Post, PostMedia, Comentario
from django.contrib import messages
import json
from .utils_notificaciones import (
    crear_notificacion_like,
    crear_notificacion_comentario
)


def muro_noticias(request):

    # ⚠ BLOQUEA POST SI NO ESTÁ LOGUEADO
    if request.method == 'POST' and not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para publicar.")
        return redirect('noticias:muro')

    # ✔ Crear publicación si está logueado
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()

            # Guardar medios
            archivos = request.FILES.getlist('media')
            for i, archivo in enumerate(archivos):
                ext = archivo.name.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    tipo = 'imagen'
                elif ext in ['mp4', 'webm', 'mov', 'avi', 'mkv']:
                    tipo = 'video'
                else:
                    continue

                PostMedia.objects.create(
                    post=post,
                    archivo=archivo,
                    tipo=tipo,
                    orden=i
                )

            messages.success(request, "¡Tu publicación ha sido creada!")
            return redirect('noticias:muro')
    else:
        form = PostForm()

    posts = Post.objects.filter(activo=True).select_related('autor').prefetch_related('medios', 'comentarios', 'likes')

    contexto = {
        'form': form,
        'posts': posts,
        'comentario_form': ComentarioForm(),
    }
    return render(request, 'noticias/muro.html', contexto)



@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id, activo=True)
    user = request.user

    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

        # 🔔 Crear notificación (solo si no se da like a sí mismo)
        crear_notificacion_like(user, post)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'total_likes': post.total_likes,
        })

    return redirect('noticias:muro')


@login_required
def lista_likes(request, post_id):
    """Devuelve en JSON los usuarios que dieron like a un post."""
    post = get_object_or_404(Post, pk=post_id, activo=True)

    likes = []
    for u in post.likes.all():
        nombre = u.get_full_name() or u.first_name or u.username
        likes.append({
            "id": u.id,
            "nombre": nombre,
        })

    return JsonResponse({"likes": likes})

@login_required
def lista_comentarios(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Solo comentarios raíz
    comentarios_root = post.comentarios.filter(padre__isnull=True).order_by("creado_en")

    # Convertir todo a JSON recursivamente
    data = {
        "comentarios": [serialize_comentario(c, request.user) for c in comentarios_root]
    }

    return JsonResponse(data)

def serialize_comentario(com, user):
    return {
        "id": com.id,
        "autor": com.autor.get_full_name() or com.autor.username,
        "texto": com.texto,
        "fecha": timesince(com.creado_en) + " atrás",
        "total_likes": com.total_likes,
        "liked_by_user": user in com.likes.all(),
        "respuestas": [
            serialize_comentario(r, user) 
            for r in com.respuestas.all().order_by("creado_en")
        ]
    }


@login_required
def toggle_like_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    user = request.user

    if user in comentario.likes.all():
        comentario.likes.remove(user)
        liked = False
    else:
        comentario.likes.add(user)
        liked = True

        # 🔔 Crear notificación SOLO cuando es like nuevo
        from .utils_notificaciones import crear_notificacion_like_comentario
        crear_notificacion_like_comentario(user, comentario)

    return JsonResponse({
        'liked': liked,
        'total_likes': comentario.total_likes
    })


@login_required
def agregar_comentario(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        padre_id = request.POST.get("padre_id")  # <-- respuestas

        if texto:
            comentario = Comentario.objects.create(
                post=post,
                autor=request.user,
                texto=texto,
                padre_id=padre_id if padre_id else None
            )

            # 🔔 Crear notificación de comentario / respuesta
            crear_notificacion_comentario(request.user, comentario)

            return redirect("noticias:muro")

    return redirect("noticias:muro")


@login_required
def responder_comentario(request, comentario_id):
    parent = get_object_or_404(Comentario, id=comentario_id)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        if texto == "":
            return JsonResponse({"error": "Texto vacío"}, status=400)

        nueva_respuesta = Comentario.objects.create(
            post=parent.post,
            autor=request.user,
            texto=texto,
            padre=parent
        )

        # 🔔 Notificación correspondiente (respuesta a comentario)
        from .utils_notificaciones import crear_notificacion_respuesta
        crear_notificacion_respuesta(request.user, nueva_respuesta)

        return JsonResponse({
            "success": True,
            "id": nueva_respuesta.id,
            "post_id": parent.post.id,
            "parent_id": parent.id,
            "autor": request.user.get_full_name() or request.user.username,
            "texto": nueva_respuesta.texto,
            "fecha": nueva_respuesta.creado_en.strftime("%d/%m/%Y %H:%M"),
            "total_respuestas": parent.respuestas.count()
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)




@login_required
def editar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, autor=request.user)

    if request.method == "POST":
        contenido = request.POST.get("contenido", "").strip()

        # Archivos nuevos
        nuevos_archivos = request.FILES.getlist("nuevo_media")

        # IDs de medios eliminados
        eliminar = request.POST.getlist("eliminar_media[]")

        # Actualizar texto
        post.contenido = contenido
        post.save()

        # Eliminar medios marcados
        if eliminar:
            PostMedia.objects.filter(id__in=eliminar, post=post).delete()

        # Agregar nuevos medios
        for archivo in nuevos_archivos:
            tipo = "imagen"
            if archivo.content_type.startswith("video"):
                tipo = "video"

            PostMedia.objects.create(
                post=post,
                archivo=archivo,
                tipo=tipo
            )

        return JsonResponse({
            "success": True,
            "html": contenido.replace("\n", "<br>")
        })

    return JsonResponse({"success": False})



@login_required
@require_POST
def eliminar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, autor=request.user)

    post.delete()

    return JsonResponse({"success": True})


def obtener_media_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    data = []
    for m in post.medios.all():
        data.append({
            "id": m.id,
            "url": m.archivo.url,
            "tipo": m.tipo
        })

    return JsonResponse({"medios": data})


@login_required
def eliminar_media(request, media_id):
    media = get_object_or_404(PostMedia, id=media_id, post__autor=request.user)

    media.archivo.delete()
    media.delete()

    return JsonResponse({"success": True})


@login_required
def leer_notificacion(request, notif_id):
    notif = get_object_or_404(Notificacion, id=notif_id, usuario=request.user)

    notif.leido = True
    notif.save()

    return redirect(notif.get_url())

@login_required
def historial_notificaciones(request):
    # últimas 5 notificaciones (leídas o no)
    historial = Notificacion.objects.filter(
        usuario=request.user
    ).order_by("-creado_en")[:5]

    return render(request, "noticias/historial_notificaciones.html", {
        "historial": historial
    })

