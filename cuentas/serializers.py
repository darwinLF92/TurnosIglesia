from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction, IntegrityError
import re
from usuarios.models import UserProfile
from .tokens import make_email_token, read_email_token, make_reset_password_token
from nucleo.correos import enviar_confirmacion_correo
from django.core.signing import BadSignature, SignatureExpired
from django.contrib.auth.password_validation import validate_password
from nucleo.correos import enviar_reset_password_correo
from datetime import date, timezone
from devotos.models import Devoto


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
            "fecha_nacimiento","genero", "estatura", "telefono", "correo"
        )

    # -------------------------
    # VALIDACIONES POR CAMPO
    # -------------------------

    def validate_cui(self, value):
        if not re.match(r"^\d{13}$", value):
            raise serializers.ValidationError("El CUI debe tener exactamente 13 dígitos numéricos.")

        if UserProfile.objects.filter(cui=value).exists():
            raise serializers.ValidationError("El CUI ya está registrado.")

        return value

    def validate_usuario(self, value):
        username = value  # <-- CORRECCIÓN

        if not re.match(r"^[A-Za-z0-9]{1,16}$", username):
            raise serializers.ValidationError("El usuario solo puede contener letras y números (máx. 16).")

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Este usuario ya está en uso.")

        return value

    def validate_correo(self, value):
        email = value  # <-- CORRECCIÓN

        if len(email) > 100:
            raise serializers.ValidationError("El correo no puede exceder 50 caracteres.")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")

        return value

    def validate_nombres(self, value):
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{1,50}$", value):
            raise serializers.ValidationError("Nombres inválidos.")
        return value

    def validate_apellidos(self, value):
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{1,50}$", value):
            raise serializers.ValidationError("Apellidos inválidos.")
        return value

    def validate_direccion(self, value):
        if value and len(value) > 100:
            raise serializers.ValidationError("La dirección no puede exceder 100 caracteres.")
        return value

    def validate_estatura(self, value):
        if value is not None and (value < 50 or value > 250):
            raise serializers.ValidationError("Estatura fuera de rango (50–250).")
        return value

    def validate_telefono(self, value):
        if value and not re.match(r"^\d{8}$", value):
            raise serializers.ValidationError("El teléfono debe tener 8 dígitos.")
        return value

    def validate_fecha_nacimiento(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("La fecha no puede ser futura.")
        return value
    
    def validate_genero(self, value):
        if value not in ["M", "F", "O"]:
            raise serializers.ValidationError("Género inválido.")
        return value

    # -------------------------
    # CREATE
    # -------------------------
    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")

        try:
            # 1. Crear usuario
            user = User.objects.create(
                username=user_data["username"],
                email=user_data["email"],
                first_name=validated_data.get("nombres", ""),
                last_name=validated_data.get("apellidos", ""),
                is_active=True,
            )
            user.set_unusable_password()
            user.save()

            # 2. Crear perfil
            perfil = UserProfile.objects.create(
                user=user,
                **validated_data,
                correo_verificado=False,
                estado=True,
            )

                    # 3️⃣ Crear o reutilizar DEVOTO
            nombre_completo = f"{perfil.nombres or ''} {perfil.apellidos or ''}".strip()

            devoto, creado = Devoto.objects.get_or_create(
                cui_o_nit=perfil.cui,
                defaults={
                    "nombre": nombre_completo,
                    "correo": user.email,
                    "telefono": perfil.telefono or "",
                    "direccion": perfil.direccion or "",
                    "fecha_nacimiento": perfil.fecha_nacimiento,
                    "activo": True,
                    "usuario_registro": user,
                }
            )

            # Si ya existía, opcionalmente sincronizar datos
            if not creado:
                devoto.nombre = nombre_completo
                devoto.correo = user.email
                devoto.telefono = perfil.telefono or devoto.telefono
                devoto.direccion = perfil.direccion or devoto.direccion
                devoto.fecha_nacimiento = perfil.fecha_nacimiento
                devoto.usuario_modificacion = user
                devoto.fecha_modificacion = timezone.now()
                devoto.save()


            # 3. Asignar grupo
            grupo, _ = Group.objects.get_or_create(name="Usuario")
            user.groups.add(grupo)

            # 4. Generar token
            token = make_email_token(user.id)

            # 5. Enviar correo dentro del TRY (si falla → rollback)
            enviar_confirmacion_correo(user, token)

        except Exception as e:
            # Cualquier falla genera rollback total
            raise serializers.ValidationError(
                {"detalle": f"Error al registrar usuario: {str(e)}"}
            )

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