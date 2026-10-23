from decimal import Decimal

from django.db import models


class ConfiguracionTienda(models.Model):
    """Parámetros generales que el administrador puede ajustar (registro único)."""

    nombre_tienda = models.CharField(max_length=100, default='Dlune Pijamas')
    telefono_whatsapp = models.CharField(max_length=20, blank=True)
    impuesto_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=19)
    costo_domicilio_base = models.DecimalField(max_digits=10, decimal_places=2, default=8000)
    vip_min_compras = models.PositiveIntegerField(default=5, help_text='Compras para ser VIP')
    vip_min_gastado = models.DecimalField(max_digits=12, decimal_places=2, default=500000, help_text='Monto gastado para ser VIP')
    dias_cliente_inactivo = models.PositiveIntegerField(default=60)

    class Meta:
        verbose_name = 'configuración de la tienda'
        verbose_name_plural = 'configuración de la tienda'

    def __str__(self):
        return self.nombre_tienda

    @classmethod
    def obtener(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config

    def calcular_impuesto(self, subtotal):
        return (Decimal(subtotal) * self.impuesto_porcentaje / Decimal('100')).quantize(Decimal('1'))
