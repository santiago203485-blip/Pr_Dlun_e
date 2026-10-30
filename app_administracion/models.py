from decimal import Decimal

from django.db import models


class ConfiguracionTienda(models.Model):
    """Parámetros generales que el administrador puede ajustar (registro único)."""

    nombre_tienda = models.CharField(max_length=100, default='Dlune Pijamas')
    eslogan = models.CharField(max_length=150, blank=True, default='Pijamas con estampados para toda la familia.')
    telefono_whatsapp = models.CharField(max_length=20, blank=True)
    telefono_fijo = models.CharField(max_length=20, blank=True)
    email_contacto = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    horario = models.CharField(max_length=150, blank=True, help_text='Ej: Lunes a sábado de 9:00 a. m. a 7:00 p. m.')
    instagram = models.CharField(max_length=60, blank=True, help_text='Usuario sin @')
    facebook = models.CharField(max_length=100, blank=True, help_text='Usuario o nombre de la página')
    tiktok = models.CharField(max_length=60, blank=True, help_text='Usuario sin @')
    nombre_responsable = models.CharField(max_length=120, blank=True, help_text='Dueña o persona de contacto')
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

    @property
    def enlace_whatsapp(self):
        numero = ''.join(ch for ch in self.telefono_whatsapp if ch.isdigit())
        if len(numero) == 10:
            numero = '57' + numero
        return f'https://wa.me/{numero}' if numero else ''

    @property
    def tiene_contacto(self):
        return any([self.telefono_whatsapp, self.telefono_fijo, self.email_contacto, self.direccion, self.horario])

    def calcular_impuesto(self, subtotal):
        return (Decimal(subtotal) * self.impuesto_porcentaje / Decimal('100')).quantize(Decimal('1'))
