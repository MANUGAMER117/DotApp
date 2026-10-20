from django.contrib import admin
from .models import (
    Usuario, Perfil, Dotacion, Bodega, Inventario, Reserva,
    Entrega, AlertaPreventiva, Devolucion, Operador,
)

admin.site.register([
    Usuario, Perfil, Dotacion, Bodega, Inventario, Reserva,
    Entrega, AlertaPreventiva, Devolucion, Operador,
])
