from django import forms
from .models import Establecimiento

class EstablecimientoForm(forms.ModelForm):
    class Meta:
        model = Establecimiento
        fields = ['nombre', 'hermandad', 'direccion', 'telefono', 'email', 'sitio_web', 'logo', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'hermandad': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.logo:
            self.fields['logo'].help_text = (
                f'<a href="{self.instance.logo.url}" target="_blank" class="btn btn-info btn-sm">Ver logo actual</a>'
            )