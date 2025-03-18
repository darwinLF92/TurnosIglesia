from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Devoto
from .forms import DevotoForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse

class ListaDevotosView(ListView):
    model = Devoto
    template_name = 'devotos/lista_devotos.html'
    context_object_name = 'object_list'
    paginate_by = 8  # Número de elementos por página

    def get_queryset(self):
        queryset = Devoto.objects.all().order_by('nombre')  # Ordenar alfabéticamente por nombre
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(codigo__icontains=query) |
                Q(cui_o_nit__icontains=query) |
                Q(nombre__icontains=query)
            ).order_by('nombre')  # Asegurar que también esté ordenado tras la búsqueda
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')  # Mantener el valor en el campo de búsqueda
        return context

class CrearDevotoView(CreateView):
    model = Devoto
    form_class = DevotoForm
    template_name = 'devotos/crear_devoto.html'

    def form_valid(self, form):
        """
        Si el formulario es válido, guarda el devoto y muestra un mensaje de éxito.
        """
        form.save()
        messages.success(self.request, "Devoto creado correctamente.")
        return self.render_to_response(self.get_context_data(form=form, success=True, message="Devoto creado correctamente."))

    def form_invalid(self, form):
        """
        Si hay errores en el formulario, los muestra en SweetAlert sin redirigir.
        """
        messages.error(self.request, "Hubo un error al crear el devoto. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))


class EditarDevotoView(UpdateView):
    model = Devoto
    form_class = DevotoForm
    template_name = 'devotos/editar_devoto.html'

    def form_valid(self, form):
        """
        Si el formulario es válido, actualiza el devoto y muestra un mensaje de éxito.
        """
        form.save()
        messages.success(self.request, "Devoto actualizado correctamente.")
        return self.render_to_response(self.get_context_data(form=form, success=True, message="Devoto actualizado correctamente."))

    def form_invalid(self, form):
        """
        Si hay errores en el formulario, los muestra en SweetAlert sin redirigir.
        """
        messages.error(self.request, "Hubo un error al actualizar el devoto. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))


class EliminarDevotoView(DeleteView):
    model = Devoto
    template_name = 'devotos/eliminar_devoto.html'

    def delete(self, request, *args, **kwargs):
        """
        Si la eliminación es exitosa, muestra un mensaje de éxito.
        """
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "Devoto eliminado exitosamente.")
        return self.render_to_response(self.get_context_data(success=True, message="Devoto eliminado correctamente."))
