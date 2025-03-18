from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Establecimiento
from .forms import EstablecimientoForm

@method_decorator(login_required, name='dispatch')
class EstablecimientoListView(ListView):
    model = Establecimiento
    template_name = 'establecimiento/lista_establecimientos.html'
    context_object_name = 'establecimientos'

@method_decorator(login_required, name='dispatch')
class EstablecimientoCreateView(CreateView):
    model = Establecimiento
    form_class = EstablecimientoForm
    template_name = 'establecimiento/formulario_establecimiento.html'
    success_url = reverse_lazy('establecimiento:lista_establecimientos')

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class EstablecimientoUpdateView(UpdateView):
    model = Establecimiento
    form_class = EstablecimientoForm
    template_name = 'establecimiento/formulario_establecimiento.html'
    success_url = reverse_lazy('establecimiento:lista_establecimientos')

@method_decorator(login_required, name='dispatch')
class EstablecimientoDeleteView(DeleteView):
    model = Establecimiento
    template_name = 'establecimiento/eliminar_establecimiento.html'
    success_url = reverse_lazy('establecimiento:lista_establecimientos')
