from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    cargo = models.CharField(max_length=100, default='Colaborador')
    activo = models.BooleanField(default=True)
    fecha_contratacion = models.DateField()

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    talla_vestido = models.CharField(max_length=10, default='M')
    talla_calzado = models.CharField(max_length=10, default='40')
    preferencia_ergonomica = models.CharField(max_length=100, blank=True)
    requerimientos = models.TextField(blank=True)
    proxima_entrega = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.usuario.nombre}'


class Bodega(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Dotacion(models.Model):
    sku = models.CharField(max_length=30, unique=True, default='SKU-PENDIENTE')
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    talla = models.CharField(max_length=10, blank=True)
    punto_reorden = models.PositiveIntegerField(default=5)

    class Meta:
        ordering = ['nombre', 'talla']

    def __str__(self):
        label = self.nombre
        if self.talla:
            label += f' - Talla {self.talla}'
        return label

    @property
    def stock_total(self):
        return self.inventarios.aggregate(total=models.Sum('cantidad'))['total'] or 0

    @property
    def sugerencia_compra(self):
        demanda = Usuario.objects.filter(activo=True).count()
        return max(0, demanda + self.punto_reorden - self.stock_total)


class Inventario(models.Model):
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='inventarios')
    dotacion = models.ForeignKey(Dotacion, on_delete=models.CASCADE, related_name='inventarios')
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['bodega', 'dotacion'], name='uniq_bodega_dotacion')]

    def __str__(self):
        return f'{self.dotacion} / {self.bodega}: {self.cantidad}'


class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    dotacion = models.ForeignKey(Dotacion, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateTimeField(default=timezone.now)
    fecha_programada = models.DateField(null=True, blank=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_reserva']


class Entrega(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='entrega')
    firma_data = models.TextField()
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    identificador_receptor = models.CharField(max_length=120, blank=True)
    acta_numero = models.CharField(max_length=40, unique=True)
    fecha_entrega = models.DateTimeField(default=timezone.now)
    ip_receptor = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_entrega']


class AlertaPreventiva(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='alertas')
    dotacion = models.ForeignKey(Dotacion, on_delete=models.CASCADE, related_name='alertas')
    fecha_emision = models.DateTimeField(default=timezone.now)
    fecha_programada = models.DateField(null=True, blank=True)
    mensaje = models.TextField()
    enviada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_emision']


class Devolucion(models.Model):
    CAUSALES = [
        ('talla', 'Cambio de talla'),
        ('defecto', 'Defecto de fábrica'),
        ('desgaste', 'Desgaste'),
        ('otro', 'Otro'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='devoluciones')
    dotacion = models.ForeignKey(Dotacion, on_delete=models.CASCADE, related_name='devoluciones')
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='devoluciones')
    causal = models.CharField(max_length=20, choices=CAUSALES)
    observaciones = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, default='recibida')

class Operador(models.Model):
    ROLES = [
        ('administrador', 'Administrador'),
        ('rh', 'Recursos Humanos'),
        ('bodega', 'Encargado de Bodega'),
        ('compras', 'Compras'),
    ]
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=30, choices=ROLES, default='bodega')
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Operador'
        verbose_name_plural = 'Operadores'

    def __str__(self):
        return f'{self.nombre} · {self.get_rol_display()}'

