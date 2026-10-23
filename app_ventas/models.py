from decimal import Decimal

from django.conf import settings
from django.db import models

from app_catalogo.models import Producto
from app_clientes.models import Cliente


class Venta(models.Model):
    """Venta registrada por un vendedor en la tienda física."""

    ACTIVA = 'activa'
    ANULADA = 'anulada'
    ESTADOS = [(ACTIVA, 'Activa'), (ANULADA, 'Anulada')]
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
        ('transferencia', 'Transferencia'),
    ]

    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ventas')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    estado = models.CharField(max_length=10, choices=ESTADOS, default=ACTIVA)

    class Meta:
        verbose_name = 'venta'
        verbose_name_plural = 'ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f'Venta #{self.id}'

    def calcular_total(self):
        from app_administracion.models import ConfiguracionTienda

        self.subtotal = sum((d.subtotal for d in self.detalles.all()), Decimal('0'))
        self.impuesto = ConfiguracionTienda.obtener().calcular_impuesto(self.subtotal)
        self.total = self.subtotal + self.impuesto
        self.save()
        return self.total

    def anular(self, usuario=None):
        """Anula la venta y devuelve las unidades al inventario."""
        from app_inventario.models import MovimientoInventario

        if self.estado == self.ANULADA:
            return False
        for detalle in self.detalles.select_related('producto'):
            MovimientoInventario.registrar(
                detalle.producto, MovimientoInventario.ENTRADA, detalle.cantidad, f'Anulación venta #{self.id}', usuario
            )
        self.estado = self.ANULADA
        self.save(update_fields=['estado'])
        return True


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'detalle de venta'
        verbose_name_plural = 'detalles de venta'

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
