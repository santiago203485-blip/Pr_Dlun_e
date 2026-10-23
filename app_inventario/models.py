from django.conf import settings
from django.db import models

from app_catalogo.models import Producto


class MovimientoInventario(models.Model):
    """Registro de entradas y salidas de stock."""

    ENTRADA = 'entrada'
    SALIDA = 'salida'
    TIPOS = [(ENTRADA, 'Entrada'), (SALIDA, 'Salida')]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=150, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'movimiento de inventario'
        verbose_name_plural = 'movimientos de inventario'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} de {self.cantidad} - {self.producto.nombre}'

    @classmethod
    def registrar(cls, producto, tipo, cantidad, motivo='', usuario=None):
        """Crea el movimiento y actualiza el stock del producto."""
        movimiento = cls.objects.create(
            producto=producto, tipo=tipo, cantidad=cantidad, motivo=motivo, usuario=usuario
        )
        producto.actualizar_stock(cantidad if tipo == cls.ENTRADA else -cantidad)
        return movimiento
