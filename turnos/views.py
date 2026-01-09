from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import TurnoForm
from .models import Turno, Procesion
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator




@method_decorator(login_required, name='dispatch')
class CrearTurnoView(CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/crear_turno.html'

    def get_initial(self):
        """
        Inicializa el formulario con:
        - la procesión seleccionada
        - el siguiente número de turno disponible
        """
        initial = super().get_initial()
        procesion_id = self.request.GET.get('procesion_id')

        if procesion_id:
            procesion = get_object_or_404(Procesion, id=procesion_id)
            initial['procesion'] = procesion

            # 🔹 Buscar el último turno creado para esa procesión
            ultimo_turno = (
                Turno.objects
                .filter(procesion=procesion)
                .order_by('-numero_turno')
                .first()
            )

            # 🔹 Sugerir el siguiente número
            if ultimo_turno:
                initial['numero_turno'] = ultimo_turno.numero_turno + 1
            else:
                initial['numero_turno'] = 1

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Turno'

        procesion_id = self.request.GET.get('procesion_id')
        if procesion_id:
            context['procesion_seleccionada'] = get_object_or_404(
                Procesion, id=procesion_id
            )

        return context

    def form_valid(self, form):
        messages.success(self.request, "¡Turno creado exitosamente!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Hubo un error al crear el turno. Verifique los datos ingresados."
        )
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        """
        Redirige nuevamente al formulario manteniendo la procesión seleccionada
        y permitiendo seguir creando turnos en secuencia.
        """
        procesion_id = self.request.GET.get('procesion_id', '')
        return reverse('turnos:crear_turno') + f"?procesion_id={procesion_id}"

@login_required    
def lista_turnos(request):
    procesion_id = request.GET.get('procesion_id')

    # 🔹 Procesiones activas, más recientes primero
    qs_procesiones = Procesion.objects.filter(activo=True).order_by('-fecha_creacion')

    # 🔹 Paginación de procesiones (por ejemplo, 10 por página)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs_procesiones, 2)
    procesiones_page = paginator.get_page(page_number)

    # 🔹 Turnos SOLO si se eligió una procesión
    turnos = None
    if procesion_id:
        turnos = Turno.objects.filter(
            procesion_id=procesion_id
        ).order_by('numero_turno')

    return render(request, 'turnos/lista_turnos.html', {
        'turnos': turnos,
        'procesiones': procesiones_page,  # ahora es una página
        'page_obj': procesiones_page,     # alias útil para el template
    })


@method_decorator(login_required, name='dispatch')
class EditarTurnoView(UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/editar_turno.html'

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "¡Turno actualizado exitosamente!")
        context = self.get_context_data(form=form)
        context['turno'] = self.object  # 🔥 Aquí pasamos el turno actualizado
        return render(self.request, self.template_name, context)

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al actualizar el turno. Verifica los datos ingresados.")
        context = self.get_context_data(form=form)
        context['turno'] = self.object if hasattr(self, 'object') else None
        return render(self.request, self.template_name, context)

@login_required
def eliminar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        turno.delete()
        return redirect('turnos:lista_turnos')
    return render(request, 'turnos/eliminar_turno.html', {'turno': turno})

@login_required
def detalle_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    
    # Filtrar solo inscripciones activas
    inscripciones_activas = turno.inscripciones.filter(inscrito=True)
    
    # Contar solo las inscripciones activas
    inscritos_count = inscripciones_activas.count()
    
    # Calcular los turnos disponibles correctamente
    turnos_disponibles = turno.capacidad - inscritos_count  

    return render(request, 'turnos/detalle_turno.html', {
        'turno': turno,
        'inscripciones': inscripciones_activas,  # Solo inscripciones activas
        'inscritos_count': inscritos_count,
        'turnos_disponibles': turnos_disponibles
    })