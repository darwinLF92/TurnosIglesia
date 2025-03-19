from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from .forms import InscripcionForm
from .models import RegistroInscripcion, Turno
from django.views.generic import ListView
from django.http import JsonResponse
from devotos.models import Devoto
from procesiones.models import Procesion
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views import View
from weasyprint import HTML
import tempfile
from django.template.loader import get_template
from establecimiento.models import Establecimiento
import os
import urllib.parse  # Importar para codificar URLs
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
import json
from weasyprint import CSS
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@login_required
def inscribir_devoto(request):
    if request.method == 'POST':
        
        form = InscripcionForm(request.POST)
        if form.is_valid():
            inscripcion = form.save(commit=False)
            inscripcion.inscrito = True  # Marca como inscrito

            # ✅ Obtener el valor del turno antes de guardar
            if inscripcion.turno:
                inscripcion.valor_turno = inscripcion.turno.valor  # Verifica que sea el campo correcto en el modelo

            inscripcion.save()
            return redirect(reverse('gestion_turnos:lista_inscripciones'))
        else:
            print("🚨 ERRORES EN EL FORMULARIO:", form.errors)
            error_message = form.non_field_errors()
            return render(request, 'gestion_turnos/crear_inscripcion.html', {
                'form': form,
                'error_message': error_message,
            })
    else:
        form = InscripcionForm()

    # Agregar la lista de devotos activos y procesiones activas al contexto
    devotos_activos = Devoto.objects.filter(activo=True) 
    procesiones = Procesion.objects.filter(activo=True)  # Suponiendo que hay un campo `activo`

    return render(request, 'gestion_turnos/crear_inscripcion.html', {
        'form': form,
        'devotos_activos': devotos_activos,
        'procesiones': procesiones  # ✅ Se pasa al contexto
    })

@login_required
def obtener_precio_turno(request):
    turno_id = request.GET.get('turno_id')
    if turno_id:
        try:
            turno = Turno.objects.get(id=turno_id)
            return JsonResponse({'precio': float(turno.valor)})  # Retorna el precio en JSON
        except Turno.DoesNotExist:
            return JsonResponse({'error': 'Turno no encontrado'}, status=404)
    return JsonResponse({'error': 'ID de turno no proporcionado'}, status=400)

@method_decorator(login_required, name='dispatch')
class ListaInscripciones(ListView): 
    model = RegistroInscripcion
    template_name = "gestion_turnos/lista_inscripciones.html"
    context_object_name = "inscripciones"
    paginate_by = 7

    def get_queryset(self):
        # Mostrar solo inscripciones activas (inscrito=True)
        queryset = RegistroInscripcion.objects.filter(
            inscrito=True
        ).select_related("devoto").order_by("-fecha_inscripcion")

        # Capturar los parámetros de búsqueda desde la URL
        nombre = self.request.GET.get("nombre", "").strip()
        cui_o_nit = self.request.GET.get("cui_o_nit", "").strip()
        fecha_inicio = self.request.GET.get("fecha_inicio", "").strip()
        fecha_fin = self.request.GET.get("fecha_fin", "").strip()

        if nombre:
            queryset = queryset.filter(devoto__nombre__icontains=nombre)

        if cui_o_nit:
            queryset = queryset.filter(devoto__cui_o_nit__icontains=cui_o_nit)

        if fecha_inicio:
            fecha_inicio = parse_date(fecha_inicio)
            if fecha_inicio:
                queryset = queryset.filter(fecha_inscripcion__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = parse_date(fecha_fin)
            if fecha_fin:
                queryset = queryset.filter(fecha_inscripcion__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page = self.request.GET.get("page", 1)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_obj = paginator.get_page(page)

        context["inscripciones"] = page_obj
        return context


@login_required
def load_turnos(request):
    procesion_id = request.GET.get('procesion_id')
    if procesion_id:
        turnos = Turno.objects.filter(procesion_id=procesion_id).values('id', 'numero_turno', 'referencia')
        return JsonResponse(list(turnos), safe=False)
    return JsonResponse([], safe=False)

@login_required
def ajax_devotos_activos(request):
    devotos = Devoto.objects.filter(activo=True).values('id', 'nombre', 'cui_o_nit')
    return JsonResponse(list(devotos), safe=False)

@login_required
def ajax_procesiones_activas(request):
    procesiones = Procesion.objects.filter(activo=True).values('id', 'nombre')
    return JsonResponse(list(procesiones), safe=False)

@login_required
def buscar_devotos_list(request):
    termino_busqueda = request.GET.get('q', '')
    devotos = Devoto.objects.filter(nombre__icontains=termino_busqueda).values('nombre')[:10]  # Limita los resultados a 10
    return JsonResponse(list(devotos), safe=False)

# Vista para anular una inscripción
@method_decorator(login_required, name='dispatch')
class AnularInscripcionView(View):
    def get(self, request, inscripcion_id):
        """Renderiza la plantilla de confirmación de anulación."""
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)
        return render(request, 'gestion_turnos/anular_inscripcion.html', {'inscripcion': inscripcion})

    def post(self, request, inscripcion_id):
        """Procesa la anulación de la inscripción."""
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)

        if not inscripcion.inscrito:
            messages.error(request, "Esta inscripción ya ha sido anulada.")
            return render(request, 'gestion_turnos/anular_inscripcion.html', {'inscripcion': inscripcion})

        # Obtener el turno asociado
        turno = inscripcion.turno

        # **Actualizar los valores del turno**
        if turno:
            turno_inscritos_actualizados = RegistroInscripcion.objects.filter(turno=turno, inscrito=True).count() - 1
            turno_disponibles_actualizados = turno.capacidad - turno_inscritos_actualizados

            # **Evitar números negativos**
            turno_inscritos_actualizados = max(turno_inscritos_actualizados, 0)
            turno_disponibles_actualizados = max(turno_disponibles_actualizados, 0)

            # **Guardar cambios en el turno**
            turno.save()

        # **Anular inscripción**
        inscripcion.inscrito = False
        inscripcion.entregado = False
        inscripcion.fecha_entrega = None
        inscripcion.save()

        messages.success(request, "Inscripción anulada correctamente.")
        return render(request, 'gestion_turnos/anular_inscripcion.html', {'inscripcion': inscripcion})
# Vista para generar el comprobante de inscripción
@method_decorator(login_required, name='dispatch')
class ComprobanteInscripcionView(View):
    def get(self, request, inscripcion_id):
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)
        html = render_to_string('gestion_turnos/comprobante_inscripcion.html', {'inscripcion': inscripcion})
        return HttpResponse(html)
    
@method_decorator(login_required, name='dispatch')
class ComprobanteRecepcionView(View):
    def get(self, request, inscripcion_id):
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)
        html = render_to_string('gestion_turnos/comprobante_recepcion.html', {'inscripcion': inscripcion})
        return HttpResponse(html)


# Vista para el detalle de inscripción
@method_decorator(login_required, name='dispatch')
class DetalleInscripcionView(View):
    def get(self, request, inscripcion_id):
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)
        return render(request, 'gestion_turnos/detalle_inscripcion.html', {'inscripcion': inscripcion})
    
@method_decorator(login_required, name='dispatch')
class ComprobanteInscripcionPDFView(View):
    def get(self, request, inscripcion_id):
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)
        establecimiento = Establecimiento.objects.filter(estado='activo').first()

        html_string = render_to_string(
            "gestion_turnos/comprobante_inscripcion_pdf.html",
            {'inscripcion': inscripcion, 'establecimiento': establecimiento}
        )

        pdf_content = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprobante_{inscripcion.id}.pdf"'
        return response

@method_decorator(login_required, name='dispatch')    
class ComprobanteRecepcionPDFView(View):
    def get(self, request, inscripcion_id):
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)
        establecimiento = Establecimiento.objects.filter(estado='activo').first()

        html_string = render_to_string(
            "gestion_turnos/comprobante_recepcion_pdf.html",
            {'inscripcion': inscripcion, 'establecimiento': establecimiento}
        )

        pdf_content = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recepcion_{inscripcion.id}.pdf"'
        return response


@method_decorator(login_required, name='dispatch')
class EnviarComprobanteWhatsAppView(View):
    def get(self, request, inscripcion_id):
        # Obtener la inscripción
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id)

        # Obtener el teléfono del devoto
        telefono_devoto = inscripcion.devoto.telefono
        if not telefono_devoto:
            return JsonResponse({"error": "El devoto no tiene un número de teléfono registrado."}, status=400)

        # Limpiar el número (solo dígitos)
        telefono_devoto = ''.join(filter(str.isdigit, telefono_devoto))

        # Obtener la procesión y turno
        nombre_procesion = inscripcion.turno.procesion.nombre
        numero_turno = inscripcion.turno.numero_turno
        fecha_entrega_estimada = inscripcion.fecha_entrega_estimada.strftime("%d-%m-%Y") if inscripcion.fecha_entrega_estimada else "No definida"
        lugar_entrega = inscripcion.lugar_entrega if inscripcion.lugar_entrega else "No definido"

        # Obtener el establecimiento
        establecimiento = Establecimiento.objects.filter(estado='activo').first()
        nombre_hermandad = establecimiento.hermandad if establecimiento else "la Hermandad"

        # Generar el PDF y guardarlo en MEDIA_ROOT
        pdf_filename = f"comprobante_{inscripcion_id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
        
        HTML(string=render_to_string("gestion_turnos/comprobante_inscripcion_pdf.html", {'inscripcion': inscripcion})).write_pdf(target=pdf_path)

        # Obtener la URL del archivo PDF y asegurar que use HTTPS
        pdf_url = request.build_absolute_uri(settings.MEDIA_URL + pdf_filename)
        pdf_url = pdf_url.replace("http://", "http://")

        # Construir el mensaje de WhatsApp con los datos relevantes
        mensaje = (
            f"Hola {inscripcion.devoto.nombre},\n\n"
            f"✅ Se ha inscrito exitosamente a la procesión *{nombre_procesion}* en el turno *{numero_turno}* con el recibo No. *{inscripcion.id}*.\n\n"
            f"📅 *Fecha de entrega:* {fecha_entrega_estimada}\n"
            f"📍 *Lugar de entrega:* {lugar_entrega}\n\n"
            f"Agradecemos su colaboración con nuestra Hermandad y, de parte de Nuestro Señor Jesucristo, le deseamos bendiciones.\n\n"
            f"🙏 Que tenga un buen y bendecido Turno.\n\n"
            f"Atentamente,\n{nombre_hermandad}.\n\n"
            f"📄 Puede descargar su comprobante aquí:\n{pdf_url}"
        )

        # Codificar correctamente el mensaje
        mensaje_codificado = urllib.parse.quote(mensaje)

        # Generar el enlace de WhatsApp
        whatsapp_url = f"https://api.whatsapp.com/send?phone={telefono_devoto}&text={mensaje_codificado}"

        # Retornar la URL de WhatsApp
        return JsonResponse({"whatsapp_url": whatsapp_url}, status=200)
    
@method_decorator(login_required, name='dispatch')
class ListaEntregaTurnos(View):
    template_name = "gestion_turnos/lista_entrega_turnos.html"

    def get(self, request):
        entregados = request.GET.get("entregados", "").lower() == "true"
        nombre = request.GET.get("nombre", "").strip()

        # Filtrar inscripciones por entregados y nombre de devoto
        inscripciones = RegistroInscripcion.objects.filter(
            inscrito=True, entregado=entregados
        ).select_related("devoto", "turno")

        if nombre:
            inscripciones = inscripciones.filter(devoto__nombre__icontains=nombre)

        # Paginación
        paginacion = request.GET.get("paginacion", 5)  # Se permite personalizar cantidad de elementos por página
        paginator = Paginator(inscripciones, paginacion)
        page = request.GET.get("page")
        inscripciones_paginadas = paginator.get_page(page)

        # Mantener los filtros en la paginación
        query_params = f"&nombre={nombre}&entregados={entregados}"

        return render(request, self.template_name, {
            "inscripciones": inscripciones_paginadas,
            "filtro_entregados": entregados,
            "nombre": nombre,
            "query_params": query_params,  # Se pasa para mantener los filtros en la paginación
        })



@method_decorator(login_required, name='dispatch')
class EntregarTurnoView(View):
    def post(self, request, inscripcion_id):
        inscripcion = get_object_or_404(RegistroInscripcion, id=inscripcion_id, inscrito=True, entregado=False)

        # Marcar como entregado
        inscripcion.entregado = True
        inscripcion.fecha_entrega = timezone.now()
        inscripcion.save()

        messages.success(request, f"Turno entregado correctamente a {inscripcion.devoto.nombre}.")
        return JsonResponse({"success": True})

@method_decorator(login_required, name='dispatch')   
class ValidarEntregaTurnoView(View):
    def post(self, request, inscripcion_id):
        try:
            data = json.loads(request.body)
            codigo_ingresado = data.get("id_inscripcion")

            # Buscar la inscripción válida (activa, no entregada)
            inscripcion = get_object_or_404(
                RegistroInscripcion,
                id=inscripcion_id,
                inscrito=True,
                entregado=False
            )

            # Validar usando el campo 'codigo'
            if str(inscripcion.codigo).strip() != str(codigo_ingresado).strip():
                return JsonResponse({
                    "success": False,
                    "message": "El código ingresado no coincide con la inscripción. Verifique e intente nuevamente."
                }, status=400)

            # Marcar como entregado
            inscripcion.entregado = True
            inscripcion.fecha_entrega = timezone.now()
            inscripcion.save()

            return JsonResponse({
                "success": True,
                "message": "Turno entregado correctamente."
            })

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "Error en la solicitud. Intente nuevamente."
            }, status=400)