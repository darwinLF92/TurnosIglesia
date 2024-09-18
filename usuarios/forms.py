from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm

class UserForm(UserCreationForm):
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label="Rol")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'grupo']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            grupo = self.cleaned_data.get('grupo')
            if grupo:
                user.groups.add(grupo)
        return user

class EditUserForm(UserChangeForm):
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label="Rol")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'grupo']

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        if self.instance:
            initial_group = self.instance.groups.first()  # Asumiendo que cada usuario tiene solo un grupo
            self.fields['grupo'].initial = initial_group

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            grupo = self.cleaned_data.get('grupo')
            if grupo:
                user.groups.clear()  # Elimina los grupos actuales antes de asignar uno nuevo
                user.groups.add(grupo)
        return user
    

class GroupPermissionForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        super(GroupPermissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['permissions'].initial = self.instance.permissions.all()