from datetime import date, timedelta
from django.core.management.base import BaseCommand
from gestion_dotaciones.models import Usuario, Perfil, Bodega, Dotacion, Inventario, Reserva, Operador


class Command(BaseCommand):
    help = 'Carga datos de demostración para DotApp.'

    def handle(self, *args, **options):
        users = [
            ('Ana Torres', 'ana.torres@demo.local', 'Operaria de campo', 'M', '38', 4),
            ('Carlos Gómez', 'carlos.gomez@demo.local', 'Técnico de mantenimiento', 'L', '41', 18),
            ('Laura Méndez', 'laura.mendez@demo.local', 'Supervisora SST', 'S', '37', 25),
            ('Juan Rojas', 'juan.rojas@demo.local', 'Auxiliar de bodega', 'M', '40', 40),
        ]
        for name, email, cargo, tv, tc, days in users:
            user, _ = Usuario.objects.update_or_create(email=email, defaults={'nombre': name, 'cargo': cargo, 'fecha_contratacion': date(2025, 1, 15), 'activo': True})
            Perfil.objects.update_or_create(usuario=user, defaults={'talla_vestido': tv, 'talla_calzado': tc, 'preferencia_ergonomica': 'Ajuste estándar', 'proxima_entrega': date.today() + timedelta(days=days)})

        principal, _ = Bodega.objects.get_or_create(nombre='Bodega Principal', defaults={'ubicacion': 'Bogotá D.C.'})
        norte, _ = Bodega.objects.get_or_create(nombre='Bodega Norte', defaults={'ubicacion': 'Bogotá D.C.'})
        items = [
            ('CHA-M-001', 'Chaleco reflectivo', 'EPP', 'M', 5),
            ('CAS-40-002', 'Casco de seguridad', 'EPP', '40', 6),
            ('CAM-L-003', 'Camisa de trabajo', 'Vestuario', 'L', 8),
            ('BOT-40-004', 'Botas de seguridad', 'Calzado', '40', 5),
            ('PAN-M-005', 'Pantalón de trabajo', 'Vestuario', 'M', 4),
        ]
        for sku, nombre, tipo, talla, minimo in items:
            item, _ = Dotacion.objects.get_or_create(sku=sku, defaults={'nombre': nombre, 'tipo': tipo, 'talla': talla, 'punto_reorden': minimo})
            if not Inventario.objects.filter(bodega=principal, dotacion=item).exists():
                Inventario.objects.create(bodega=principal, dotacion=item, cantidad=7 if sku != 'PAN-M-005' else 3)
            if not Inventario.objects.filter(bodega=norte, dotacion=item).exists():
                Inventario.objects.create(bodega=norte, dotacion=item, cantidad=2)

        ana = Usuario.objects.get(email='ana.torres@demo.local')
        chaleco = Dotacion.objects.get(sku='CHA-M-001')
        Reserva.objects.get_or_create(usuario=ana, dotacion=chaleco, estado='pendiente', defaults={'fecha_programada': date.today() + timedelta(days=3), 'observaciones': 'Entrega demo para presentación.'})
        self.stdout.write(self.style.SUCCESS('Datos demo cargados correctamente.'))
