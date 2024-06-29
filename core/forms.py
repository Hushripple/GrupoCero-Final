from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField
from django_recaptcha.fields import ReCaptchaField
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

class TipoLanzamientoForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = TipoLanzamiento
        fields = ['nombreTipo']
        widgets = {
            'nombreTipo': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_nombreTipo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'nombreTipo',
        )
        for field_name, field in self.fields.items():
            field.label = False

class LanzamientoForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Lanzamiento
        fields = ['tipoLanzamiento', 'nombreLanzamiento', 'artista', 'fechaLanzamiento', 'genero', 'descripcionLanzamiento', 'precio', 'imagen']
        widgets = {
            'tipoLanzamiento': forms.Select(attrs={'class': 'form-control'}),
            'nombreLanzamiento': forms.TextInput(attrs={'class': 'form-control'}),
            'artista': forms.Select(attrs={'class': 'form-control'}),
            'fechaLanzamiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'descripcionLanzamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['artista'].queryset = Artista.objects.filter(aprobado='aprobado')
        self.fields['genero'].queryset = GeneroMusical.objects.filter(aprobado='aprobado')
        self.fields['tipoLanzamiento'].queryset = TipoLanzamiento.objects.filter(aprobado='aprobado')

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'tipoLanzamiento',
            'nombreLanzamiento',
            'artista',
            'fechaLanzamiento',
            'genero',
            'descripcionLanzamiento',
            'precio',
            'imagen',
            'captcha',
        )
        for field_name, field in self.fields.items():
            field.label = False

class GeneroMusicalForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = GeneroMusical
        fields = ['nombreGenero']
        widgets = {
            'nombreGenero': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_nombreGenero'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'nombreGenero',
            'captcha'
        )
        for field_name, field in self.fields.items():
            field.label = False

class ArtistaForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Artista
        fields = ['nombreArtista', 'fecha_nacimiento', 'biografia', 'imagen']
        widgets = {
            'nombreArtista': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_nombreArtista'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'id': 'id_fecha_nacimiento', 'type': 'date'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'id': 'id_biografia', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'id_imagen', 'label': ''}),  
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'nombreArtista',
            'fecha_nacimiento',
            'biografia',
            'imagen',
            'captcha'
        )
        for field_name, field in self.fields.items():
            field.label = False  

class ArtistaAprobacionForm(ModelForm):
    class Meta:
        model = Artista
        fields = ['aprobado', 'feedback']

class GeneroAprobacionForm(ModelForm):
    class Meta:
        model = GeneroMusical
        fields = ['aprobado', 'feedback']

class LanzamientoAprobacionForm(ModelForm):
    class Meta:
        model = Lanzamiento
        fields = ['aprobado', 'feedback']

class TipoLanzamientoAprobacionForm(ModelForm):
    class Meta:
        model = TipoLanzamiento
        fields = ['aprobado', 'feedback']