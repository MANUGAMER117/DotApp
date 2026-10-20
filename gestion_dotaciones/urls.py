from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('operadores/', views.listar_operadores, name='listar_operadores'),
    path('operadores/nuevo/', views.crear_operador, name='crear_operador'),
    path('operadores/<int:operador_id>/editar/', views.editar_operador, name='editar_operador'),
    path('operadores/<int:operador_id>/estado/', views.cambiar_estado_operador, name='cambiar_estado_operador'),
    path('colaboradores/', views.listar_usuarios, name='listar_colaboradores'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/nuevo/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:usuario_id>/perfil/', views.editar_perfil, name='editar_perfil'),
    path('usuarios/<int:usuario_id>/reservar/', views.reservar_dotacion, name='reservar_dotacion_usuario'),
    path('usuarios/<int:usuario_id>/reservar/<int:dotacion_id>/', views.reservar_dotacion, name='reservar_dotacion'),
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('reservas/<int:reserva_id>/confirmar/', views.confirmar_reserva, name='confirmar_reserva'),
    path('reservas/<int:reserva_id>/firmar/', views.firmar_entrega, name='firmar_entrega'),
    path('entregas/<int:entrega_id>/acta.pdf', views.acta_pdf, name='acta_pdf'),
    path('inventario/', views.inventario, name='inventario'),
    path('reservas/<int:usuario_id>/emitir-alerta-preventiva/<int:dotacion_id>/', views.emitir_alerta_preventiva, name='emitir_alerta_preventiva'),
    path('devoluciones/', views.devoluciones, name='devoluciones'),
]
