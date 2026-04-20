from django.db import models
from django.contrib.auth.models import User

from datetime import datetime


def current_year():
    return datetime.now().year

# Create your models here.

# models.py

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    version_terminos = models.CharField(max_length=10, default="")
    version_privacidad = models.CharField(max_length=10, default="")

    fecha_aceptacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class Eventos(models.Model):
    titulo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    año = models.IntegerField(default=current_year)

    precio_base = models.IntegerField(default=0)

    def __str__(self):
        return self.titulo


class Estudiante(models.Model):
    GRADOS = [(g, str(g)) for g in range(1, 12)] # Añadir 1, 2, 3...
    SECCIONES = [('A', 'A'), ('B', 'B'),] # Añadir A, B, C...

    nombre = models.CharField(max_length=100)
    grado = models.IntegerField(choices=GRADOS)
    seccion = models.CharField(max_length=2, choices=SECCIONES)

    def __str__(self):
        return f"{self.nombre} {self.grado}{self.seccion}"


class Transaccion(models.Model):
    listaGrados = [(i, str(i)) for i in range(1, 12 + 1)]

    evento = models.ForeignKey(Eventos, on_delete=models.CASCADE)
    monto = models.PositiveIntegerField()
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    grado = models.IntegerField(
        choices=listaGrados
    )

    seccion = models.CharField(
        max_length=2,
        choices=[
            ('A', 'A'),
            ('B', 'B'),
        ],
        default='A'
    )

    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Evento: {self.evento} / Estudiante: {self.estudiante} / Receptor: {self.usuario}"


class Producto(models.Model):
    evento = models.ForeignKey(Eventos, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} - {self.evento.titulo}"


class DetalleTransaccion(models.Model):
    transaccion = models.ForeignKey('Transaccion', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def subtotal(self):
        return self.producto.precio * self.cantidad

class DocumentoLegal(models.Model):
    TIPO_CHOICES = [
        ('terminos', 'Términos y Condiciones'),
        ('privacidad', 'Política de Privacidad'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    version = models.CharField(max_length=10)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} v{self.version}"