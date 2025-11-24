# cuentas/forms.py

from django import forms
from django.contrib.auth.models import User
from usuarios.models import UserProfile   # 👈 MUY IMPORTANTE
from django.forms.widgets import ClearableFileInput


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

class CustomClearableFileInput(ClearableFileInput):
    template_name = "widgets/custom_file_input.html"  # lo creamos abajo



class PerfilForm(forms.ModelForm):
    foto_perfil = forms.ImageField(
        required=False,
        widget=CustomClearableFileInput
    )

    class Meta:
        model = UserProfile
        fields = [
            "foto_perfil",
            "nombres",
            "apellidos",
            "cui",
            "direccion",
            "fecha_nacimiento",
            "genero",
            "estatura",
            "telefono",
        ]
        labels = {
            "foto_perfil": "Foto de perfil",
            "nombres": "Nombres",
            "apellidos": "Apellidos",
            "cui": "CUI",
            "direccion": "Dirección",
            "fecha_nacimiento": "Fecha de nacimiento",
            "genero": "Género",
            "estatura": "Estatura (cm)",
            "telefono": "Teléfono",
        }
        widgets = {
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "cui": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "genero": forms.Select(attrs={"class": "form-control"}),
            "estatura": forms.NumberInput(attrs={"class": "form-control", "min": 100, "max": 250}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
        }
