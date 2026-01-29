# aplicacion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from establecimiento.models import Establecimiento
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Informacion, ConfiguracionHome, ImagenInformacion
from .forms import InformacionForm, ConfiguracionHomeForm
from django.views.decorators.http import require_POST
from .models import ImagenPresentacion
from .forms import ImagenPresentacionForm
from .models import MarchaFunebre, Favorito
from .forms import MarchaFunebreForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import HistoriaImagenForm
from .models import HistoriaImagen
from django.utils.http import url_has_allowed_host_and_scheme
from .models import MediaAlbum, Foto, Video
from .forms import MediaAlbumForm, FotoBulkUploadForm, VideoForm, FotoForm, VideoForm2
from django.db import transaction
from django.core.exceptions import ValidationError
from procesiones.models import Procesion, PostInformacion

def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Administrador').exists()
    )


def home_view(request):

    posts_info = PostInformacion.objects.filter(estado="activo", relevante=True).order_by("orden", "-fecha", "-id")

    imagenes = ImagenPresentacion.objects.filter(activo=True).order_by('-fecha_creacion')

    procesion_destacada = (
        Procesion.objects
        .filter(activo=True, es_relevante=True)
        .first()
    )

    establecimiento = Establecimiento.objects.first()  # 👈 obtener logo

    return render(request, 'aplicacion/home.html', {
        'imagenes_presentacion': imagenes,
        'procesion_destacada': procesion_destacada,  # 👈 CLAVE
        'logo_establecimiento': establecimiento.logo.url if establecimiento and establecimiento.logo else None,
        'posts_info': posts_info,
    })

def login_view(request):
    error_message = None
    logo_url = None
    nombre_hermandad = None

    # Verifica si hay un establecimiento
    establecimiento = Establecimiento.objects.first()
    if establecimiento and establecimiento.logo:
        logo_url = establecimiento.logo.url
        nombre_hermandad = establecimiento.hermandad

    # Si el usuario ya está autenticado, lo enviamos al home directamente
    if request.user.is_authenticated:
        return redirect('aplicacion:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Recupera el parámetro "next" si viene de una página protegida
            next_url = request.GET.get('next') or request.POST.get('next')

            # 🔔 Mensaje de bienvenida SOLO si NO viene con "next"
            if not next_url:
                nombre_mostrar = f"{user.first_name} {user.last_name}".strip() or user.username
                messages.success(
                    request,
                    f"Bienvenido(a) de nuevo, {nombre_mostrar}.",
                    extra_tags="bienvenida"
                )

            # Seguridad: verifica que "next" sea una URL válida del mismo dominio
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            # Si no hay "next", va al home
            return redirect('aplicacion:home')
        else:
            error_message = 'Usuario o contraseña inválidos'

    context = {
        'error_message': error_message,
        'logo_url': logo_url,
        'nombre_hermandad': nombre_hermandad,
        # opcional: para usarlo en un <input type="hidden" name="next">
        'next': request.GET.get('next', ''),
    }
    return render(request, 'aplicacion/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('aplicacion:home')  

# Vista para listar configuraciones
@method_decorator(login_required, name='dispatch')
class ConfiguracionHomeListView(ListView):
    model = ConfiguracionHome
    template_name = 'aplicacion/configuracion_home_list.html'
    context_object_name = 'configuraciones'  # <- Nombre simple y válido


# Vista para crear una nueva configuración
@method_decorator(login_required, name='dispatch')
class ConfiguracionHomeCreateView(CreateView):
    model = ConfiguracionHome
    form_class = ConfiguracionHomeForm
    template_name = 'aplicacion/configuracion_home_form.html'
    success_url = reverse_lazy('aplicacion:configuracion_home_list')

# Vista para editar una configuración existente
@method_decorator(login_required, name='dispatch')
class ConfiguracionHomeUpdateView(UpdateView):
    model = ConfiguracionHome
    form_class = ConfiguracionHomeForm
    template_name = 'aplicacion/configuracion_home_form.html'
    success_url = reverse_lazy('aplicacion:configuracion_home_list')

# Vista para eliminar una configuración
@method_decorator(login_required, name='dispatch')
class ConfiguracionHomeDeleteView(DeleteView):
    model = ConfiguracionHome
    template_name = 'aplicacion/configuracion_home_confirm_delete.html'
    success_url = reverse_lazy('aplicacion:configuracion_home_list')

@method_decorator(login_required, name='dispatch')
class InformacionListView(ListView):
    model = Informacion
    template_name = 'informacion_list.html'
    context_object_name = 'informacion'

@method_decorator(login_required, name='dispatch')
class InformacionCreateView(CreateView):
    model = Informacion
    form_class = InformacionForm
    template_name = 'informacion_form.html'
    success_url = reverse_lazy('inicio')

@method_decorator(login_required, name='dispatch')
class InformacionUpdateView(UpdateView):
    model = Informacion
    form_class = InformacionForm
    template_name = 'informacion_form.html'
    success_url = reverse_lazy('inicio')

@method_decorator(login_required, name='dispatch')
class InformacionDeleteView(DeleteView):
    model = Informacion
    template_name = 'informacion_confirm_delete.html'
    success_url = reverse_lazy('inicio')

def quienes_somos_view(request):
    info = Informacion.objects.last()  # O puedes usar .first() si solo habrá un registro
    config = ConfiguracionHome.objects.filter(seccion='quienes_somos', activo=True).first()
    return render(request, 'aplicacion/quienes_somos.html', {
        'info': info,
        'config': config,
    })

@login_required
def crear_informacion(request):
    if request.method == 'POST':
        form_info = InformacionForm(request.POST)
        if form_info.is_valid():
            info = form_info.save()

            # Guardar imágenes múltiples
            for img in request.FILES.getlist('imagenes'):
                ImagenInformacion.objects.create(informacion=info, imagen=img)

            return redirect('aplicacion:quienes_somos')  # o donde necesites redirigir
    else:
        form_info = InformacionForm()

    return render(request, 'aplicacion/informacion_form.html', {
        'form_info': form_info
    })

@method_decorator(login_required, name='dispatch')
class InformacionListView(ListView):
    model = Informacion
    template_name = 'aplicacion/informacion_list.html'
    context_object_name = 'informaciones'

@login_required
def editar_informacion(request, pk):
    info = get_object_or_404(Informacion, pk=pk)

    if request.method == 'POST':
        form = InformacionForm(request.POST, instance=info)

        if form.is_valid():
            form.save()

            # Agregar nuevas imágenes
            for f in request.FILES.getlist('imagenes'):
                ImagenInformacion.objects.create(informacion=info, imagen=f)

            return redirect('aplicacion:informacion_listar')  # Ajusta al nombre de tu vista de lista

    else:
        form = InformacionForm(instance=info)

    imagenes = info.imagenes.all()

    return render(request, 'aplicacion/editar_informacion.html', {
        'form': form,
        'imagenes': imagenes,
        'info': info
    })

@method_decorator(login_required, name='dispatch')
class InformacionDeleteView(DeleteView):
    model = Informacion
    template_name = 'aplicacion/informacion_confirm_delete.html'
    success_url = reverse_lazy('aplicacion:informacion_listar')

@login_required
@require_POST
def eliminar_imagen(request, pk):
    imagen = get_object_or_404(ImagenInformacion, pk=pk)
    imagen.delete()
    return redirect(request.META.get('HTTP_REFERER', 'informacion_list'))

@method_decorator(login_required, name='dispatch')
class ImagenPresentacionCreateView(CreateView):
    model = ImagenPresentacion
    form_class = ImagenPresentacionForm
    template_name = 'aplicacion/imagen_presentacion_form.html'
    success_url = reverse_lazy('aplicacion:imagen_presentacion_list')

@method_decorator(login_required, name='dispatch')
class ImagenPresentacionListView(ListView):
    model = ImagenPresentacion
    template_name = 'aplicacion/imagen_presentacion_list.html'
    context_object_name = 'imagenes'

@method_decorator(login_required, name='dispatch')
class ImagenPresentacionUpdateView(UpdateView):
    model = ImagenPresentacion
    form_class = ImagenPresentacionForm
    template_name = 'aplicacion/imagen_presentacion_form.html'
    success_url = reverse_lazy('aplicacion:imagen_presentacion_list')

@method_decorator(login_required, name='dispatch')
class ImagenPresentacionDeleteView(DeleteView):
    model = ImagenPresentacion
    template_name = 'aplicacion/imagen_presentacion_confirm_delete.html'
    success_url = reverse_lazy('aplicacion:imagen_presentacion_list')


def lista_marchas(request):
    query = request.GET.get('q', '')
    filtro = request.GET.get('filtro', 'todas')

    # Base (con búsqueda)
    marchas_base = MarchaFunebre.objects.all()
    if query:
        marchas_base = marchas_base.filter(titulo__icontains=query)

    # ✅ Total de "Todas" (respetando búsqueda)
    total_todas = marchas_base.count()

    favoritas_usuario = []
    total_favoritas = 0

    if request.user.is_authenticated:
        favoritas_usuario = Favorito.objects.filter(
            usuario=request.user
        ).values_list('marcha_id', flat=True)

        # ✅ Total de "Favoritas" (respetando búsqueda también)
        total_favoritas = marchas_base.filter(id__in=favoritas_usuario).count()

    # Aplicar filtro para listar
    marchas = marchas_base
    if filtro == 'favoritas':
        marchas = marchas.filter(id__in=favoritas_usuario)

    marchas = marchas.order_by('titulo')

    return render(request, 'aplicacion/lista_marchas.html', {
        'marchas': marchas,
        'query': query,
        'filtro': filtro,
        'favoritas_usuario': favoritas_usuario,
        'total_todas': total_todas,
        'total_favoritas': total_favoritas,
    })



@login_required(login_url='aplicacion:login')
@user_passes_test(is_admin, login_url='aplicacion:login')
def subir_marcha(request):
    if request.method == 'POST':
        form = MarchaFunebreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('aplicacion:lista_marchas')
    else:
        form = MarchaFunebreForm()
    
    return render(request, 'aplicacion/subir_marcha.html', {'form': form})

@login_required
def aumentar_favorito(request, marcha_id):
    marcha = get_object_or_404(MarchaFunebre, id=marcha_id)
    marcha.favoritos += 1
    marcha.save()
    return JsonResponse({'favoritos': marcha.favoritos})


@login_required
def toggle_favorito(request, marcha_id):
    marcha = get_object_or_404(MarchaFunebre, id=marcha_id)
    favorito, creado = Favorito.objects.get_or_create(usuario=request.user, marcha=marcha)

    if not creado:
        favorito.delete()
        estado = 'eliminado'
    else:
        estado = 'agregado'

    return JsonResponse({'estado': estado})

@login_required
def es_favorita(request, marcha_id):
    es_fav = Favorito.objects.filter(usuario=request.user, marcha_id=marcha_id).exists()
    return JsonResponse({'favorita': es_fav})

@login_required(login_url='aplicacion:login')
@user_passes_test(is_admin, login_url='aplicacion:login')
def editar_marcha(request, marcha_id):
    marcha = get_object_or_404(MarchaFunebre, id=marcha_id)

    if request.method == 'POST':
        form = MarchaFunebreForm(request.POST, request.FILES, instance=marcha)
        if form.is_valid():
            form.save()
            return render(request, 'aplicacion/editar_marcha.html', {
                'form': form,
                'success': True,
                'message': f"La marcha '{form.instance.titulo}' fue actualizada correctamente."
            })
        else:
            return render(request, 'aplicacion/editar_marcha.html', {
                'form': form,
                'message': "Hubo un error al actualizar la marcha."
            })
    else:
        form = MarchaFunebreForm(instance=marcha)

    return render(request, 'aplicacion/editar_marcha.html', {'form': form})


@login_required(login_url='aplicacion:login')
@user_passes_test(is_admin, login_url='aplicacion:login')
def eliminar_marcha(request, marcha_id):
    marcha = get_object_or_404(MarchaFunebre, id=marcha_id)

    if request.method == 'POST':
        titulo = marcha.titulo
        marcha.delete()
        messages.success(request, f"La marcha '{titulo}' fue eliminada correctamente.")
        return render(request, 'aplicacion/editar_marcha.html', {
            'form': None,
            'marcha_eliminada': True,
            'titulo_marcha': titulo
        })

    return render(request, 'aplicacion/eliminar_marcha.html', {
        'marcha': marcha
    })

from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
import os
import urllib.parse

def serve_audio(request, filename):
    filename = urllib.parse.unquote(filename)  # por si contiene %20 o caracteres especiales

    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    if not os.path.exists(file_path):
        return HttpResponseNotFound("Archivo no encontrado")

    # Soporte para reproducir con barra de progreso
    range_header = request.headers.get('Range', None)
    file_size = os.path.getsize(file_path)
    start = 0
    end = file_size - 1

    if range_header:
        start = int(range_header.replace('bytes=', '').split('-')[0])

    length = end - start + 1

    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(length)

    response = HttpResponse(data, status=206 if range_header else 200, content_type='audio/mpeg')
    response['Content-Length'] = str(length)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
    return response


# Página pública (o visible con login, como prefieras)
def historia_imagenes_view(request):
    items = HistoriaImagen.objects.filter(activo=True).order_by('orden','-fecha_creacion')
    return render(request, 'aplicacion/historia_imagenes.html', {'items': items})

# CRUD solo para usuarios con permisos
class HistoriaImagenListView(LoginRequiredMixin, ListView):
    model = HistoriaImagen
    template_name = 'aplicacion/historia_imagenes_list.html'
    context_object_name = 'items'
    permission_required = 'aplicacion.view_historiaimagen'   # ver el listado
    raise_exception = True

class HistoriaImagenCreateView(LoginRequiredMixin, CreateView):
    model = HistoriaImagen
    form_class = HistoriaImagenForm
    template_name = 'aplicacion/historia_imagenes_form.html'
    success_url = reverse_lazy('aplicacion:historia_imagenes_admin')
    permission_required = 'aplicacion.add_historiaimagen'
    raise_exception = True

class HistoriaImagenUpdateView(LoginRequiredMixin, UpdateView):
    model = HistoriaImagen
    form_class = HistoriaImagenForm
    template_name = 'aplicacion/historia_imagenes_form.html'
    success_url = reverse_lazy('aplicacion:historia_imagenes_admin')
    permission_required = 'aplicacion.change_historiaimagen'
    raise_exception = True

class HistoriaImagenDeleteView(LoginRequiredMixin, DeleteView):
    model = HistoriaImagen
    template_name = 'aplicacion/historia_imagenes_confirm_delete.html'
    success_url = reverse_lazy('aplicacion:historia_imagenes_admin')
    permission_required = 'aplicacion.delete_historiaimagen'
    raise_exception = True

# Página principal (tabs)
def galeria_view(request):
    fotos_albums = MediaAlbum.objects.filter(activo=True, tipo=MediaAlbum.FOTO)
    videos_albums = MediaAlbum.objects.filter(activo=True, tipo=MediaAlbum.VIDEO)
    return render(request, 'aplicacion/galeria.html', {
        'fotos_albums': fotos_albums,
        'videos_albums': videos_albums
    })

# Detalle de álbum (muestra fotos o videos según tipo)
#vistas para el apartado de fototeca y videos
def album_detalle_view(request, pk):
    album = get_object_or_404(MediaAlbum, pk=pk, activo=True)
    return render(request, 'aplicacion/album_detalle.html', {'album': album})

# --------- ADMIN / PANEL ----------
class AlbumListView(LoginRequiredMixin, ListView):
    model = MediaAlbum
    template_name = 'aplicacion/album_list.html'
    context_object_name = 'albumes'
    permission_required = 'aplicacion.view_mediaalbum'

class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = MediaAlbum
    form_class = MediaAlbumForm
    template_name = 'aplicacion/album_form.html'
    success_url = reverse_lazy('aplicacion:album_admin')
    permission_required = 'aplicacion.add_mediaalbum'

class AlbumUpdateView(LoginRequiredMixin, UpdateView):
    model = MediaAlbum
    form_class = MediaAlbumForm
    template_name = 'aplicacion/album_form.html'
    success_url = reverse_lazy('aplicacion:album_admin')
    permission_required = 'aplicacion.change_mediaalbum'

class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = MediaAlbum
    template_name = 'aplicacion/album_confirm_delete.html'
    success_url = reverse_lazy('aplicacion:album_admin')
    permission_required = 'aplicacion.delete_mediaalbum'

# Subir varias fotos a un álbum
@login_required
def album_foto_upload_view(request, pk):
    album = get_object_or_404(MediaAlbum, pk=pk, tipo=MediaAlbum.FOTO)

    if request.method == 'POST':
        archivos = request.FILES.getlist('imagenes')  # << clave
        if not archivos:
            messages.error(request, 'No seleccionaste ningún archivo.')
            return render(request, 'aplicacion/foto_upload_form.html', {'album': album})

        guardadas, errores = 0, 0
        try:
            with transaction.atomic():
                for f in archivos:
                    try:
                        Foto.objects.create(album=album, imagen=f)
                        guardadas += 1
                    except Exception as e:
                        errores += 1
                        messages.error(request, f'Error guardando {f.name}: {e}')
        except Exception as e:
            messages.error(request, f'Error general guardando archivos: {e}')
            return render(request, 'aplicacion/foto_upload_form.html', {'album': album})

        if guardadas:
            messages.success(request, f'{guardadas} foto(s) agregada(s).')
            if errores:
                messages.warning(request, f'{errores} archivo(s) no se pudieron subir.')
            return redirect('aplicacion:album_detalle', pk=album.pk)

        messages.error(request, 'No se pudo guardar ninguna foto.')
        return render(request, 'aplicacion/foto_upload_form.html', {'album': album})

    return render(request, 'aplicacion/foto_upload_form.html', {'album': album})

# Subir video a un álbum (URL o archivo)

def album_video_upload_view(request, pk):
    album = get_object_or_404(MediaAlbum, pk=pk, tipo=MediaAlbum.VIDEO)
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            vid = form.save(commit=False)
            vid.album = album
            vid.save()
            messages.success(request, 'Video agregado al álbum.')
            return redirect('aplicacion:album_detalle', pk=album.pk)
        else:
            messages.error(request, 'El formulario no es válido. Revisa los campos.')
    else:
        form = VideoForm()
    return render(request, 'aplicacion/video_upload_form.html', {'album': album, 'form': form})


# ------- FOTOS -------
class FotoUpdateView(LoginRequiredMixin, UpdateView):
    model = Foto
    form_class = FotoForm
    template_name = 'aplicacion/foto_form.html'

    def get_success_url(self):
        return reverse_lazy('aplicacion:album_detalle', kwargs={'pk': self.object.album.pk})

class FotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Foto
    template_name = 'aplicacion/foto_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('aplicacion:album_detalle', kwargs={'pk': self.object.album.pk})

# ------- VIDEOS -------
class VideoUpdateView(LoginRequiredMixin, UpdateView):
    model = Video
    form_class = VideoForm2
    template_name = 'aplicacion/video_form.html'

    def get_success_url(self):
        return reverse_lazy('aplicacion:album_detalle', kwargs={'pk': self.object.album.pk})

class VideoDeleteView(LoginRequiredMixin, DeleteView):
    model = Video
    template_name = 'aplicacion/video_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('aplicacion:album_detalle', kwargs={'pk': self.object.album.pk})