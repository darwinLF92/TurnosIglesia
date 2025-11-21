from django.urls import path
from .views import RegistroView, confirmar_correo, crear_contrasena, confirmar_correo_html, solicitar_reset_password, confirmar_reset_password
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView
from . import views

app_name = "cuentas"

urlpatterns = [
    # =======================
    #   ENDPOINTS DE API
    # =======================
    path("api/registro/", RegistroView.as_view(), name="api_registro"),
    path("api/confirmar-correo/", confirmar_correo, name="api_confirmar_correo"),
    path("api/crear-contrasena/", crear_contrasena, name="api_crear_contrasena"),

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/actualizar/", TokenRefreshView.as_view(), name="token_refresh"),

     path('auth/confirmar/', confirmar_correo_html, name='confirmar_correo_html'),

    # =======================
    #   PÁGINAS HTML
    # =======================
    path(
        "registro/",
        TemplateView.as_view(template_name="cuentas/registro.html"),
        name="registro_html",
    ),

    # API para solicitar reset
    path("api/olvide-password/", solicitar_reset_password, name="api_olvide_password"),

    # Formulario HTML "Olvidé mi contraseña"
    path(
        "olvide-password/",
        TemplateView.as_view(template_name="cuentas/olvide_password.html"),
        name="olvide_password_html"
    ),

    path(
        "cuentas/confirmar-password/",
        confirmar_reset_password,
        name="confirmar_reset_password",
    ),

    path("ver/", views.ver_perfil, name="perfil"),
    path("editar/", views.editar_perfil, name="editar_perfil"),
    path("cambiar-password/", views.cambiar_password, name="cambiar_password"),
]
