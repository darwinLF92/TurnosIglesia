from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import password_validators_help_texts
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
class UserForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput,
        help_text=_(
            "Tu contraseña debe cumplir con los siguientes requisitos:"
            "<ul>"
            "<li>No debe ser demasiado similar a tu información personal.</li>"
            "<li>Debe contener al menos 8 caracteres.</li>"
            "<li>No puede ser una contraseña comúnmente utilizada.</li>"
            "<li>No puede ser completamente numérica.</li>"
            "</ul>"
        ),
    )
    password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        widget=forms.PasswordInput,
        help_text=_("Introduce la misma contraseña para confirmarla."),
    )
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label=_("Rol")
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'grupo']
        labels = {
            'username': _("Nombre de usuario"),
            'email': _("Correo electrónico"),
            'first_name': _("Nombre"),
            'last_name': _("Apellido"),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            grupo = self.cleaned_data.get('grupo')
            if grupo:
                user.groups.add(grupo)
        return user
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        username = self.cleaned_data.get('username')

        try:
            validate_password(password, user=self.instance)
        except ValidationError as e:
            translated_errors = [
                _("La contraseña no puede ser demasiado similar al nombre de usuario.") if msg == "The password is too similar to the username." else msg
                for msg in e.messages
            ]
            raise ValidationError(translated_errors)

        return password
    
class EditUserForm(UserChangeForm):
    password1 = forms.CharField(
        label=_("Nueva contraseña"),
        widget=forms.PasswordInput,
        required=False,
        help_text=_("Déjalo en blanco si no deseas cambiar la contraseña."),
    )
    password2 = forms.CharField(
        label=_("Confirmar nueva contraseña"),
        widget=forms.PasswordInput,
        required=False,
        help_text=_("Introduce la misma contraseña solo si deseas cambiarla."),
    )
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label=_("Rol"),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'grupo', 'password1', 'password2']
        labels = {
            'username': _("Nombre de usuario"),
            'email': _("Correo electrónico"),
            'first_name': _("Nombre"),
            'last_name': _("Apellido"),
        }
        help_texts = {
            'username': _("Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_"),
        }

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        if self.instance:
            initial_group = self.instance.groups.first()
            self.fields['grupo'].initial = initial_group

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if not password:
            return None

        try:
            validate_password(password, user=self.instance)
        except ValidationError as e:
            raise ValidationError(e.messages)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden."))

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # 🔹 Solo cambiar la contraseña si se ingresó una nueva
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)

        # 🔹 Actualizar grupo del usuario
        grupo = self.cleaned_data.get('grupo')
        if grupo:
            user.groups.clear()
            user.groups.add(grupo)

        if commit:
            user.save()  # 🔹 Aquí guardamos el usuario correctamente

        return user


    

class GroupPermissionForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("Permisos")
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': _("Nombre del grupo"),
        }

    def __init__(self, *args, **kwargs):
        super(GroupPermissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['permissions'].initial = self.instance.permissions.all()
