# views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import Procesion
from .forms import ProcesionForm
from django.contrib import messages

class ListaProcesionesView(ListView):
    model = Procesion
    template_name = 'procesiones/lista_procesiones.html'
    context_object_name = 'procesiones'

    # Filtramos por procesiones activas
    def get_queryset(self):
        return Procesion.objects.filter(activo=True)


class CrearProcesionView(CreateView):
    model = Procesion
    form_class = ProcesionForm
    template_name = 'procesiones/crear_procesion.html'

    def form_valid(self, form):
        """
        Si el formulario es válido, guarda la procesión y muestra un mensaje de éxito.
        """
        form.save()
        messages.success(self.request, "Procesión creada correctamente.")
        return self.render_to_response(self.get_context_data(form=form, success=True, message="Procesión creada correctamente."))

    def form_invalid(self, form):
        """
        Si hay errores en el formulario, los muestra en SweetAlert sin redirigir.
        """
        messages.error(self.request, "Hubo un error al crear la procesión. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))

class EditarProcesionView(UpdateView):
    model = Procesion
    form_class = ProcesionForm
    template_name = 'procesiones/editar_procesion.html'

    def form_valid(self, form):
        """
        Si el formulario es válido, actualiza la procesión y muestra un mensaje de éxito.
        """
        form.save()
        messages.success(self.request, "Procesión actualizada correctamente.")
        return self.render_to_response(self.get_context_data(form=form, success=True, message="Procesión actualizada correctamente."))

    def form_invalid(self, form):
        """
        Si hay errores en el formulario, los muestra en SweetAlert sin redirigir.
        """
        messages.error(self.request, "Hubo un error al actualizar la procesión. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))

def EliminarProcesionView(request, pk):
    procesion = get_object_or_404(Procesion, pk=pk)
    if request.method == 'POST':
        procesion.activo = False
        procesion.save()
        return redirect('procesiones:lista_procesiones')
    return render(request, 'procesiones/eliminar_procesion.html', {'procesion': procesion})
