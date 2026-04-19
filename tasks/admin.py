from django.contrib import admin
from .models import Eventos, Transaccion, Producto, DetalleTransaccion, Estudiante

# Register your models here.
admin.site.register(Eventos)
admin.site.register(Transaccion)
admin.site.register(Producto)
admin.site.register(DetalleTransaccion)
admin.site.register(Estudiante)