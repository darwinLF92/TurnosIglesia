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


def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Administrador').exists()
    )


def home_view(request):
    imagenes = ImagenPresentacion.objects.filter(activo=True).order_by('-fecha_creacion')
    return render(request, 'aplicacion/home.html', {
        'imagenes_presentacion': imagenes,
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
            next_url = request.GET.get('next')

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

    if query:
        marchas = MarchaFunebre.objects.filter(titulo__icontains=query)
    else:
        marchas = MarchaFunebre.objects.all()

    favoritas_usuario = []
    if request.user.is_authenticated:
        favoritas_usuario = Favorito.objects.filter(usuario=request.user).values_list('marcha_id', flat=True)

    if filtro == 'favoritas':
        marchas = marchas.filter(id__in=favoritas_usuario)

    # ✅ Ordenar siempre por título (nombre)
    marchas = marchas.order_by('titulo')

    return render(request, 'aplicacion/lista_marchas.html', {
        'marchas': marchas,
        'query': query,
        'filtro': filtro,
        'favoritas_usuario': favoritas_usuario,
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

