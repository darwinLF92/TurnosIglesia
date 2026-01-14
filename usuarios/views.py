from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import UserForm, GroupPermissionForm
from django.contrib.auth.models import User
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from .models import GroupStatus
from .forms import EditUserForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from usuarios.models import UserProfile
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def crear_usuario(request):
    grupos = Group.objects.all()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()  # Ya incluye la asignación del grupo
            return render(request, 'crear_usuario.html', {
                'success': True,
                'message': 'Usuario creado satisfactoriamente',
                'form': UserForm(),
                'grupos': grupos
            })
        else:
            return render(request, 'crear_usuario.html', {
                'form': form,
                'grupos': grupos
            })
    else:
        form = UserForm()
    return render(request, 'crear_usuario.html', {'form': form, 'grupos': grupos})


@login_required
def lista_usuarios(request):
    search = request.GET.get('search', '')
    grupo = request.GET.get('grupo', '')
    paginacion = request.GET.get('paginacion', 8)  # 👈 cantidad por página (default 10)

    # Todos los usuarios activos (para el contador general)
    total_activos = User.objects.filter(is_active=True).count()

    # Query base
    usuarios_list = User.objects.filter(is_active=True)

    # 🔍 Filtro por texto
    if search:
        usuarios_list = usuarios_list.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )

    # 🎯 Filtro por grupo
    if grupo:
        usuarios_list = usuarios_list.filter(groups__name=grupo)

    usuarios_list = usuarios_list.order_by('username')

    # 👇 Usa 'paginacion' para el Paginator
    paginator = Paginator(usuarios_list, int(paginacion))
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)

    grupos = Group.objects.all().order_by('name')

    return render(request, 'lista_usuarios.html', {
        'usuarios': usuarios,
        'grupos': grupos,
        'search': search,
        'grupo': grupo,
        'total_activos': total_activos,
        'paginacion': int(paginacion),  # 👈 lo mandamos al template
    })



@login_required
def editar_usuario(request, user_id):
    user_instance = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user_instance)
        if form.is_valid():
            user = form.save(commit=False)

            # 🔹 Corregimos el nombre del campo para obtener el grupo
            grupo = form.cleaned_data.get('grupo')
            if grupo:
                user.groups.clear()
                user.groups.add(grupo)

            # 🔹 Actualizar la contraseña si se proporciona
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
                update_session_auth_hash(request, user)  # Mantiene la sesión activa

            user.save()  # 🔹 Guardamos correctamente el usuario aquí
            
            return render(request, 'editar_usuario.html', {
                'form': form,
                'success': True,
                'message': f'Usuario {form.instance.username} editado satisfactoriamente'
            })
        else:
            return render(request, 'editar_usuario.html', {
                'form': form,
                'error_message': 'Error inesperado, intente nuevamente'
            })
    else:
        form = EditUserForm(instance=user_instance)

    return render(request, 'editar_usuario.html', {'form': form})

class InactivarUsuarioView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'inactivar_usuario.html'
    fields = ['is_active']

    def form_valid(self, form):
        usuario = form.save(commit=False)

        # 1) Inactivar usuario base
        usuario.is_active = False
        usuario.save()

        # 2) Inactivar su perfil también
        try:
            perfil = UserProfile.objects.get(user=usuario)
            perfil.estado = False
            perfil.save()
        except UserProfile.DoesNotExist:
            # Si por alguna razón no tiene perfil, simplemente lo ignoramos
            pass

        messages.success(
            self.request,
            f'El usuario {usuario.username} ha sido inactivado correctamente.'
        )

        return self.render_to_response(self.get_context_data(form=form, success=True))

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al inactivar el usuario. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))


class ListaRolesView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'lista_roles.html'
    context_object_name = 'roles'

    def get_queryset(self):
        """
        Filtra los roles activos usando el modelo GroupStatus.
        Solo se muestran los roles donde `is_active=True`
        """
        return Group.objects.filter(groupstatus__is_active=True)

class CrearRolView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ['name']
    template_name = 'form_rol.html'

    def form_valid(self, form):
        # Guardar el formulario pero no redirigir
        form.save()

        # Agregar mensaje de éxito
        messages.success(self.request, f'El rol "{form.instance.name}" ha sido creado correctamente.')

        # Volver a renderizar la misma página con mensaje
        return self.render_to_response(self.get_context_data(form=form, success=True))

    def form_invalid(self, form):
        # Agregar mensaje de error
        messages.error(self.request, "Hubo un error al crear el rol. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))
    
@login_required
def editar_role(request, pk):
    grupo = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        form = GroupPermissionForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            return render(request, 'editar_role.html', {
                'success': True,
                'message': f'El rol "{grupo.name}" ha sido actualizado correctamente.',
                'form': form,
                'grupo': grupo
            })
        else:
            return render(request, 'editar_role.html', {
                'form': form,
                'grupo': grupo
            })
    else:
        form = GroupPermissionForm(instance=grupo)

    return render(request, 'editar_role.html', {'form': form, 'grupo': grupo})

class InactivarRolView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = []
    template_name = 'inactivar_rol.html'

    def form_valid(self, form):
        # Buscar el estado del grupo y marcarlo como inactivo
        status, created = GroupStatus.objects.get_or_create(group=self.object)
        status.is_active = False
        status.save()

        messages.success(self.request, f'El rol "{self.object.name}" ha sido inactivado correctamente.')

        return self.render_to_response(self.get_context_data(form=form, success=True))

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al inactivar el rol. Inténtelo de nuevo.")
        return self.render_to_response(self.get_context_data(form=form, success=False))

    
@login_required
def lista_usuarios_inactivos_modal(request):
    usuarios_inactivos = User.objects.filter(is_active=False).order_by("username")
    paginator = Paginator(usuarios_inactivos, 5)  # 5 por página

    page = request.GET.get("page")
    usuarios = paginator.get_page(page)

    return render(request, "usuarios_inactivos_modal.html", {
        "usuarios": usuarios,
    })


@login_required
def activar_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)

    # 1) Activar el usuario base
    usuario.is_active = True
    usuario.save()

    # 2) Activar también el perfil (si existe)
    try:
        perfil = UserProfile.objects.get(user=usuario)
        perfil.estado = True
        perfil.save()
    except UserProfile.DoesNotExist:
        pass

    messages.success(
        request,
        f"El usuario {usuario.username} ha sido activado correctamente."
    )

    # 👇 Muy importante:
    # Como esta vista se usa dentro del iframe del modal, lo mandamos
    # de regreso a la lista de usuarios inactivos (la versión para modal)
    return redirect("usuarios:lista_usuarios_inactivos_modal")

@login_required
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    username = usuario.username

    usuario.delete()  # elimina User y por CASCADE el UserProfile

    messages.success(
        request,
        f"El usuario {username} ha sido eliminado definitivamente."
    )

    return redirect("usuarios:lista_usuarios_inactivos_modal")
