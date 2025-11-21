from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from usuarios.models import UserProfile
from .serializers import (
    RegistroSerializer, ConfirmarCorreoSerializer, CrearContrasenaSerializer, Usuario
)
from django.shortcuts import render
from .serializers import SolicitarResetPasswordSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.signing import BadSignature, SignatureExpired
from .tokens import make_reset_password_token, read_reset_password_token
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PerfilForm, UsuarioForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse

class RegistroView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistroSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            print("❌ Registro errores:", ser.errors)  # <-- log temporal
            raise serializers.ValidationError(ser.errors)
        self.perform_create(ser)
        return Response(ser.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def confirmar_correo(request):
    s = ConfirmarCorreoSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
    s.save()
    return Response({"detalle": "Correo confirmado."}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def crear_contrasena(request):
    s = CrearContrasenaSerializer(data=request.data)
    if not s.is_valid():
        print("❌ crear_contrasena errores:", s.errors)  # temporal para ver el detalle en la consola
        raise serializers.ValidationError(s.errors)
    s.save()
    return Response({"detalle": "Contraseña creada. Ya puedes iniciar sesión."}, status=status.HTTP_200_OK)

def confirmar_correo_html(request):
    """
    GET  -> valida token, marca correo como verificado y muestra formulario de contraseña.
    POST -> recibe correo + password1/password2, crea la contraseña.
    """
    contexto = {
        "estado": "",     # 'error_confirmacion', 'form_password', 'password_ok'
        "mensaje": "",
        "correo": "",
        "errores": None,
    }

    if request.method == "GET":
        token = request.GET.get("token")
        correo = request.GET.get("correo", "")
        contexto["correo"] = correo

        if not token:
            contexto["estado"] = "error_confirmacion"
            contexto["mensaje"] = "Token no proporcionado."
            return render(request, "cuentas/confirmar_correo.html", contexto)

        # Usamos tu serializer de confirmación
        s = ConfirmarCorreoSerializer(data={"token": token})
        if not s.is_valid():
            contexto["estado"] = "error_confirmacion"
            contexto["mensaje"] = "; ".join(
                f"{k}: {v}" for k, v in s.errors.items()
            )
            return render(request, "cuentas/confirmar_correo.html", contexto)

        # Marca el correo como verificado
        s.save()

        contexto["estado"] = "form_password"
        contexto["mensaje"] = "Correo confirmado. Ahora crea tu contraseña."
        return render(request, "cuentas/confirmar_correo.html", contexto)

    # ----- POST: crear contraseña -----
    correo = request.POST.get("correo", "")
    contexto["correo"] = correo

    s_pwd = CrearContrasenaSerializer(data={
        "correo": correo,
        "password1": request.POST.get("password1"),
        "password2": request.POST.get("password2"),
    })

    if s_pwd.is_valid():
        s_pwd.save()
        contexto["estado"] = "password_ok"
        contexto["mensaje"] = "Contraseña creada correctamente. Ya puedes iniciar sesión."
        return render(request, "cuentas/confirmar_correo.html", contexto)

    contexto["estado"] = "form_password"
    contexto["mensaje"] = "Hay errores en el formulario."
    contexto["errores"] = s_pwd.errors
    return render(request, "cuentas/confirmar_correo.html", contexto)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def solicitar_reset_password(request):
    s = SolicitarResetPasswordSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
    s.save()
    return Response(
        {"detalle": "Si el correo existe y es válido, se ha enviado un enlace para restablecer la contraseña."},
        status=status.HTTP_200_OK
    )

def confirmar_reset_password(request):
    """
    /cuentas/confirmar-password/?token=...
    Muestra formulario de nueva contraseña y la guarda si es válido.
    """
    token = request.GET.get("token") or request.POST.get("token")
    contexto = {"estado": "form", "token": token}

    if not token:
        contexto["estado"] = "error"
        contexto["mensaje"] = "Token de restablecimiento no proporcionado."
        return render(request, "cuentas/password_reset_confirmar.html", contexto)

    # 1) Intentar leer el token y obtener el user_id
    try:
        user_id = read_reset_password_token(token)
    except SignatureExpired:
        contexto["estado"] = "error"
        contexto["mensaje"] = "El enlace ha expirado. Solicita un nuevo restablecimiento."
        return render(request, "cuentas/password_reset_confirmar.html", contexto)
    except BadSignature:
        contexto["estado"] = "error"
        contexto["mensaje"] = "Token inválido. El enlace de restablecimiento no es válido."
        return render(request, "cuentas/password_reset_confirmar.html", contexto)

    # 2) Buscar usuario
    try:
        usuario = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        contexto["estado"] = "error"
        contexto["mensaje"] = "Usuario no encontrado para este enlace."
        return render(request, "cuentas/password_reset_confirmar.html", contexto)

    # 3) GET → mostrar formulario
    if request.method == "GET":
        contexto["correo"] = usuario.email
        return render(request, "cuentas/password_reset_confirmar.html", contexto)

    # 4) POST → validar y guardar nueva contraseña
    password1 = request.POST.get("password1", "")
    password2 = request.POST.get("password2", "")
    errores = {}

    if password1 != password2:
        errores["password2"] = ["Las contraseñas no coinciden."]

    if not password1:
        errores.setdefault("password1", []).append("La contraseña es obligatoria.")

    if not errores:
        try:
            validate_password(password1, usuario)
        except DjangoValidationError as e:
            errores["password1"] = list(e.messages)

    if errores:
        contexto["estado"] = "form"
        contexto["errores"] = errores
        contexto["correo"] = usuario.email
        return render(request, "cuentas/password_reset_confirmar.html", contexto)

    # 5) Todo OK → guardar
    usuario.set_password(password1)
    usuario.save(update_fields=["password"])

    contexto["estado"] = "ok"
    contexto["mensaje"] = "Tu contraseña ha sido actualizada correctamente."
    contexto["correo"] = usuario.email
    return render(request, "cuentas/password_reset_confirmar.html", contexto)


@login_required
def ver_perfil(request):
    perfil = request.user.perfil
    return render(request, "cuentas/perfil.html", {"perfil": perfil})

@login_required
def editar_perfil(request):

    perfil, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest" and "remove_photo" in request.POST:
        perfil.foto_perfil.delete(save=True)
        return JsonResponse({"success": True, "action": "removed"})

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest" and "upload_photo" in request.POST:
        file = request.FILES.get("foto_perfil")
        if file:
            perfil.foto_perfil = file
            perfil.save()
            return JsonResponse({
                "success": True,
                "action": "uploaded",
                "image_url": perfil.foto_perfil.url
            })

    if request.method == "POST":
        form_usuario = UsuarioForm(request.POST, instance=request.user)
        form_perfil = PerfilForm(request.POST, request.FILES, instance=perfil)

        if form_usuario.is_valid() and form_perfil.is_valid():
            form_usuario.save()
            form_perfil.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect("cuentas:perfil")

    else:
        form_usuario = UsuarioForm(instance=request.user)
        form_perfil = PerfilForm(instance=perfil)

    return render(request, "cuentas/editar_perfil.html", {
        "form_usuario": form_usuario,
        "form_perfil": form_perfil
    })

@login_required
def cambiar_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            usuario = form.save()
            update_session_auth_hash(request, usuario)
            messages.success(request, "Contraseña actualizada correctamente")
            return redirect("cuentas:perfil")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "cuentas/cambiar_password.html", {"form": form})