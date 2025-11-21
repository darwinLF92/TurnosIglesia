from django import forms
from .models import Post, Comentario
from .widgets import MultiFileInput  # IMPORTANTE


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['contenido']  # 👈 solo el texto
        widgets = {
            'contenido': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': '¿Qué está pasando?',
                'class': 'form-control'
            })
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Escribe un comentario...',
                'class': 'form-control'
            })
        }