from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import InscripcionForm
from .models import RegistroInscripcion, Turno
from django.views.generic import ListView
from django.http import JsonResponse

def inscribir_devoto(request):
    if request.method == 'POST':
        form = InscripcionForm(request.POST)
        if form.is_valid():
            inscripcion = form.save(commit=False)
            inscripcion.inscrito = True
            inscripcion.save()
            return redirect(reverse('gestion_turnos:lista_inscripciones'))
    else:
        form = InscripcionForm()

    return render(request, 'gestion_turnos/crear_inscripcion.html', {'form': form})


class ListaInscripciones(ListView):
    model = RegistroInscripcion
    template_name = 'gestion_turnos/lista_inscripciones.html'

def load_turnos(request):
    procesion_id = request.GET.get('procesion_id')
    turnos = Turno.objects.filter(procesion_id=procesion_id).order_by('numero_turno')
    return JsonResponse(list(turnos.values('id', 'numero_turno')), safe=False)