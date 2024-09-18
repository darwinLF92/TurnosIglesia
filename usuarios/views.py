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


def crear_usuario(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')  # Redirigir a la lista de usuarios después de crear
    else:
        form = UserForm()

    return render(request, 'crear_usuario.html', {'form': form})

def lista_usuarios(request):
    usuarios = User.objects.filter(is_active=True)
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})


def editar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')
    else:
        form = EditUserForm(instance=user)
    return render(request, 'editar_usuario.html', {'form': form})

class InactivarUsuarioView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'inactivar_usuario.html'
    fields = ['is_active']  # Esto presupone que solo necesitas cambiar el estado de 'is_active'

    def form_valid(self, form):
        # Inactivar el usuario, no eliminar
        usuario = form.save(commit=False)
        usuario.is_active = False
        usuario.save()
        return redirect('usuarios:lista_usuarios')


class ListaRolesView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'lista_roles.html'
    context_object_name = 'roles'

class CrearRolView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ['name']
    template_name = 'form_rol.html'
    success_url = reverse_lazy('usuarios:lista_roles')

def editar_role(request, pk):
    grupo = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupPermissionForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect(reverse('usuarios:lista_roles'))
    else:
        form = GroupPermissionForm(instance=grupo)

    return render(request, 'editar_role.html', {'form': form, 'grupo': grupo})

class InactivarRolView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = []
    template_name = 'inactivar_rol.html'
    success_url = reverse_lazy('usuarios:lista_roles')

    def form_valid(self, form):
        # Inactivar el grupo
        status, created = GroupStatus.objects.get_or_create(group=self.object)
        status.is_active = False
        status.save()
        return super().form_valid(form)
    
