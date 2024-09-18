# views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import Procesion
from .forms import ProcesionForm

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
    success_url = reverse_lazy('procesiones:lista_procesiones')

class EditarProcesionView(UpdateView):
    model = Procesion
    form_class = ProcesionForm
    template_name = 'procesiones/editar_procesion.html'
    success_url = reverse_lazy('procesiones:lista_procesiones')

def EliminarProcesionView(request, pk):
    procesion = get_object_or_404(Procesion, pk=pk)
    if request.method == 'POST':
        procesion.activo = False
        procesion.save()
        return redirect('procesiones:lista_procesiones')
    return render(request, 'procesiones/eliminar_procesion.html', {'procesion': procesion})
