from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import TurnoForm
from .models import Turno, Procesion
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render

class CrearTurnoView(CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/crear_turno.html'
    success_url = reverse_lazy('turnos:lista_turnos')  # Asegúrate de definir esta URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Turno'
        return context
    
def lista_turnos(request):
    procesion_id = request.GET.get('procesion_id')  # Obtiene el ID de la procesión desde la URL
    turnos = None  # Inicializa turnos como None
    procesiones = Procesion.objects.all()  # Obtiene todas las procesiones para el menú desplegable

    if procesion_id:  # Verifica si hay un ID de procesión
        turnos = Turno.objects.filter(procesion_id=procesion_id)

    return render(request, 'turnos/lista_turnos.html', {'turnos': turnos, 'procesiones': procesiones})

class EditarTurnoView(UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/editar_turno.html'
    success_url = reverse_lazy('turnos:lista_turnos')  # Asegúrate de definir esta URL

def eliminar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        turno.delete()
        return redirect('turnos:lista_turnos')
    return render(request, 'turnos/eliminar_turno.html', {'turno': turno})

def detalle_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    
    # Obtener los devotos inscritos
    inscripciones = turno.inscripciones.all()  # Usamos related_name para acceder a las inscripciones
    
    # Contar cuántos devotos están inscritos
    inscritos_count = inscripciones.count()
    
    # Calcular los turnos disponibles
    turnos_disponibles = turno.capacidad - inscritos_count  # Suponiendo que el modelo Turno tiene un campo capacidad

    return render(request, 'turnos/detalle_turno.html', {
        'turno': turno,
        'inscripciones': inscripciones,
        'inscritos_count': inscritos_count,
        'turnos_disponibles': turnos_disponibles
    })
