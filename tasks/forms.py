from django.forms import ModelForm
from .models import Transaccion, Eventos, Estudiante
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['evento', 'estudiante']
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-select'}),
            'estudiante': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_estudiante'
            }),
        }

class EventoForm(forms.ModelForm):
    class Meta:
        model = Eventos
        fields = ['titulo', 'descripcion', 'precio_base']

        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del evento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción',
                'rows': 3
            }),
            'precio_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Precio base'
            }),
        }

        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'precio_base': 'Precio base (si no hay productos)',
        }

class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la contraseña'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'grado', 'seccion']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'grado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'seccion': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

        labels = {
            'nombre': 'Nombre',
            'grado': 'Grado',
            'seccion': 'Sección',
        }