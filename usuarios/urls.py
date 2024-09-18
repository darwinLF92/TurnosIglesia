from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('lista-usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('editar-usuario/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('inactivar-usuario/<int:pk>/', views.InactivarUsuarioView.as_view(), name='inactivar_usuario'),
    path('roles/', views.ListaRolesView.as_view(), name='lista_roles'),
    path('roles/nuevo/', views.CrearRolView.as_view(), name='crear_rol'),
    path('roles/editar/<int:pk>/', views.editar_role, name='editar_rol'),
    path('roles/inactivar/<int:pk>/', views.InactivarRolView.as_view(), name='inactivar_rol'),
]