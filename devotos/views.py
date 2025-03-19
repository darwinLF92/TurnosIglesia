from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Devoto
from .forms import DevotoForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.utils import timezone
import base64
from django.core.files.base import ContentFile

@method_decorator(login_required, name='dispatch')
class ListaDevotosView(ListView):
    model = Devoto
    template_name = 'devotos/lista_devotos.html'
    context_object_name = 'object_list'
    paginate_by = 8

    def get_queryset(self):
        queryset = Devoto.objects.filter(activo=True).order_by('nombre')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(codigo__icontains=query) |
                Q(cui_o_nit__icontains=query) |
                Q(nombre__icontains=query)
            ).order_by('nombre')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context



@method_decorator(login_required, name='dispatch')
class CrearDevotoView(CreateView):
    model = Devoto
    form_class = DevotoForm
    template_name = 'devotos/crear_devoto.html'
    success_url = reverse_lazy('crear_devoto')

    def form_valid(self, form):
        devoto = form.save(commit=False)
        devoto.usuario_registro = self.request.user

        foto_base64 = self.request.POST.get('foto_capturada')
        if foto_base64:
            format, imgstr = foto_base64.split(';base64,')
            ext = format.split('/')[-1]
            devoto.fotografia = ContentFile(base64.b64decode(imgstr), name='foto_capturada.' + ext)

        devoto.save()
        messages.success(self.request, "Devoto creado correctamente.")
        return self.render_to_response(self.get_context_data(form=self.form_class()))

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al crear el devoto. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form))

@method_decorator(login_required, name='dispatch')
class EditarDevotoView(UpdateView):
    model = Devoto
    form_class = DevotoForm
    template_name = 'devotos/editar_devoto.html'

    def form_valid(self, form):
        devoto = form.save(commit=False)
        devoto.usuario_modificacion = self.request.user
        devoto.fecha_modificacion = timezone.now()
        devoto.save()
        messages.success(self.request, "Devoto actualizado correctamente.")
        # Se vuelve a mostrar el formulario con los datos actualizados
        return self.render_to_response(self.get_context_data(form=form, success=True))

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al actualizar el devoto. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))


@method_decorator(login_required, name='dispatch')
class EliminarDevotoView(View):
    template_name = 'devotos/eliminar_devoto.html'

    def get(self, request, *args, **kwargs):
        devoto = get_object_or_404(Devoto, pk=kwargs['pk'])
        return render(request, self.template_name, {'object': devoto})

    def post(self, request, *args, **kwargs):
        devoto = get_object_or_404(Devoto, pk=kwargs['pk'])

        if devoto.activo:
            devoto.activo = False
            devoto.usuario_eliminacion = request.user  # 👈 Guarda quién lo desactivó
            devoto.fecha_eliminacion = timezone.now()  # 👈 Y cuándo
            devoto.save()
            success = True
            message = f"El devoto {devoto.nombre} ha sido desactivado correctamente."
        else:
            success = False
            message = f"El devoto {devoto.nombre} ya estaba desactivado."

        context = {
            'object': devoto,
            'success': success,
            'message': message,
        }
        return render(request, self.template_name, context)
