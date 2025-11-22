from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction, IntegrityError

from usuarios.models import UserProfile
from .tokens import make_email_token, read_email_token, make_reset_password_token
from nucleo.correos import enviar_confirmacion_correo
from django.core.signing import BadSignature, SignatureExpired
from django.contrib.auth.password_validation import validate_password
from nucleo.correos import enviar_reset_password_correo

Usuario = get_user_model()  # auth.User


class RegistroSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source="user.username")
    correo = serializers.EmailField(source="user.email")

    fecha_nacimiento = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d/%m/%Y"]
    )

    class Meta:
        model = UserProfile
        fields = (
            "cui", "usuario", "nombres", "apellidos", "direccion",
            "fecha_nacimiento", "estatura", "telefono", "correo"
        )

    def validate(self, attrs):
        user_data = attrs["user"]

        username = user_data.get("username")
        email = user_data.get("email")

        # Validar usuario único
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                "usuario": "Este nombre de usuario ya está en uso."
            })

        # Validar correo único
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "correo": "Este correo ya está registrado."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")

        user = User.objects.create(
            username=user_data["username"],
            email=user_data["email"],
            first_name=validated_data.get("nombres", ""),
            last_name=validated_data.get("apellidos", ""),
            is_active=True,
        )
        user.set_unusable_password()
        user.save()

        perfil = UserProfile.objects.create(
            user=user,
            **validated_data,
            correo_verificado=False,
            estado=True,
        )

        grupo, _ = Group.objects.get_or_create(name="Usuario")
        user.groups.add(grupo)

        # Correo de confirmación
        token = make_email_token(user.id)
        transaction.on_commit(lambda: enviar_confirmacion_correo(user, token))

        return perfil



class ConfirmarCorreoSerializer(serializers.Serializer):
    token = serializers.CharField()

    def save(self, **kwargs):
        token = self.validated_data["token"]
        try:
            user_id = read_email_token(token)
        except SignatureExpired:
            raise serializers.ValidationError({"detalle": "El enlace ha expirado, solicita uno nuevo."})
        except BadSignature:
            raise serializers.ValidationError({"detalle": "Token inválido."})

        try:
            u = Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"detalle": "Usuario no encontrado."})

        try:
            perfil = u.perfil  # related_name="perfil" en UserProfile
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"detalle": "Perfil de usuario no encontrado."})

        perfil.correo_verificado = True
        perfil.save(update_fields=["correo_verificado"])
        return u


class CrearContrasenaSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)
    password1 = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)
    password2 = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)

    def validate(self, attrs):
        pwd = attrs.get("password")
        p1 = attrs.get("password1")
        p2 = attrs.get("password2")

        if not pwd and not p1:
            raise serializers.ValidationError({"password": "Debes enviar 'password' o 'password1/password2'."})

        if p1 is not None:
            if p1 != p2:
                raise serializers.ValidationError({"password2": "Las contraseñas no coinciden."})
            pwd = p1

        validate_password(pwd)
        attrs["password_final"] = pwd
        return attrs

    def save(self, **kwargs):
        correo = self.validated_data["correo"]
        pwd = self.validated_data["password_final"]

        try:
            u = Usuario.objects.get(email=correo)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"correo": "Usuario no encontrado."})

        try:
            perfil = u.perfil
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"detalle": "Perfil de usuario no encontrado."})

        if not perfil.correo_verificado:
            raise serializers.ValidationError({"detalle": "Debes confirmar tu correo antes de crear la contraseña."})

        u.set_password(pwd)
        u.save(update_fields=["password"])
        return u


class SolicitarResetPasswordSerializer(serializers.Serializer):
    correo = serializers.EmailField()

    def validate_correo(self, value):
        try:
            user = Usuario.objects.get(email=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("No existe un usuario con este correo electrónico.")

        # Opcional: validar solo si el correo ya fue verificado y el user está activo
        try:
            perfil = user.perfil  # related_name="perfil" en UserProfile
            if not perfil.correo_verificado:
                raise serializers.ValidationError("El correo aún no ha sido verificado.")
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("No se encontró el perfil asociado al usuario.")

        if not user.is_active:
            raise serializers.ValidationError("El usuario está inactivo. Contacta al administrador.")

        # Guardamos para usar en save()
        self.user = user
        return value

    def save(self, **kwargs):
        user = self.user
        # Puedes usar el mismo make_email_token o crear otro tipo make_reset_token
        token = make_reset_password_token(user.id)
        enviar_reset_password_correo(user, token)
        return user