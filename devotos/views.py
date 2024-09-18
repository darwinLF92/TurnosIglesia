from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Devoto
from .forms import DevotoForm

class ListaDevotosView(ListView):
    model = Devoto
    template_name = 'devotos/lista_devotos.html'

class CrearDevotoView(CreateView):
    model = Devoto
    form_class = DevotoForm
    template_name = 'devotos/crear_devoto.html'
    success_url = reverse_lazy('devotos:lista_devotos')

class EditarDevotoView(UpdateView):
    model = Devoto
    form_class = DevotoForm
    template_name = 'devotos/editar_devoto.html'
    success_url = reverse_lazy('devotos:lista_devotos')

class EliminarDevotoView(DeleteView):
    model = Devoto
    template_name = 'devotos/eliminar_devoto.html'
    success_url = reverse_lazy('devotos:lista_devotos')
