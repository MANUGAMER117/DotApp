from datetime import date
from django.test import TestCase
from django.urls import reverse
import base64
from .models import Usuario, Perfil, Bodega, Dotacion, Inventario, Reserva, Operador


class DotAppFlowTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create(nombre='Ana Demo', email='ana@example.com', cargo='Operaria', fecha_contratacion=date(2026, 1, 10))
        Perfil.objects.create(usuario=self.user, talla_vestido='M', talla_calzado='38')
        self.bodega = Bodega.objects.create(nombre='Bodega Principal', ubicacion='Bogotá')
        self.item = Dotacion.objects.create(sku='CHA-M-001', nombre='Chaleco reflectivo', tipo='EPP', talla='M', punto_reorden=2)
        self.stock = Inventario.objects.create(bodega=self.bodega, dotacion=self.item, cantidad=3)

    def test_dashboard_and_users(self):
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('listar_colaboradores')).status_code, 200)
        self.assertEqual(self.client.get('/colaboradores/').status_code, 200)
        self.assertEqual(self.client.get('/usuarios/').status_code, 200)

    def test_reservation(self):
        response = self.client.post(reverse('reservar_dotacion_usuario', args=[self.user.id]), {'dotacion': self.item.id, 'fecha_programada': '2026-10-01', 'observaciones': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reserva.objects.count(), 1)

    def test_inventory_entry(self):
        response = self.client.post(reverse('inventario'), {'bodega': self.bodega.id, 'dotacion': self.item.id, 'cantidad': 2})
        self.assertEqual(response.status_code, 302)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.cantidad, 5)

    def test_delivery_generates_record_and_reduces_stock(self):
        reserva = Reserva.objects.create(usuario=self.user, dotacion=self.item, estado='confirmada')
        png_1x1 = base64.b64encode(b'not-a-real-image').decode()
        response = self.client.post(reverse('firmar_entrega', args=[reserva.id]), {'firma_data': 'data:image/png;base64,' + png_1x1, 'inventario_id': self.stock.id, 'identificador_receptor': self.user.email, 'latitud': '4.609710', 'longitud': '-74.081750'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))
        reserva.refresh_from_db()
        self.stock.refresh_from_db()
        self.assertEqual(reserva.estado, 'entregada')
        self.assertEqual(self.stock.cantidad, 2)
        self.assertTrue(hasattr(reserva, 'entrega'))

class OperadorTests(TestCase):
    def test_operator_crud_and_toggle(self):
        self.assertEqual(self.client.get(reverse('listar_operadores')).status_code, 200)
        response = self.client.post(reverse('crear_operador'), {
            'nombre': 'Operador Prueba',
            'email': 'operador@example.com',
            'rol': 'bodega',
            'activo': 'on',
            'fecha_alta': '2026-10-05',
        })
        self.assertEqual(response.status_code, 302)
        operator = Operador.objects.get(email='operador@example.com')
        response = self.client.post(reverse('cambiar_estado_operador', args=[operator.id]))
        self.assertEqual(response.status_code, 302)
        operator.refresh_from_db()
        self.assertFalse(operator.activo)
