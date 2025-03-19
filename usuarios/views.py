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


@login_required
def crear_usuario(request):
    grupos = Group.objects.all()  # Obtener todos los grupos disponibles
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = form.cleaned_data.get('grupo')
            if group:
                user.groups.add(group)
            return render(request, 'crear_usuario.html', {
                'success': True,
                'message': 'Usuario creado satisfactoriamente',
                'form': UserForm(),  # Formulario limpio
                'grupos': grupos
            })
        else:
            return render(request, 'crear_usuario.html', {
                'form': form,  # Formulario con datos ingresados
                'grupos': grupos
            })
    else:
        form = UserForm()

    return render(request, 'crear_usuario.html', {'form': form, 'grupos': grupos})

@login_required
def lista_usuarios(request):
    usuarios = User.objects.filter(is_active=True)
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

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
    fields = ['is_active']  # Permitir la edición del estado

    def form_valid(self, form):
        usuario = form.save(commit=False)
        usuario.is_active = False
        usuario.save()

        # 🔹 Agregar mensaje de éxito usando Django Messages
        messages.success(self.request, f'El usuario {usuario.username} ha sido inactivado correctamente.')

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

    
