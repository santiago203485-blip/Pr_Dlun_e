from django.db import models

from app_clientes.models import Cliente


class ZonaDomicilio(models.Model):
    """Ciudades/barrios con cobertura y su costo de envío."""

    ciudad = models.CharField(max_length=80)
    barrio = models.CharField(max_length=80, blank=True, help_text='Vacío = toda la ciudad')
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'zona de domicilio'
        verbose_name_plural = 'zonas de domicilio'
        ordering = ['ciudad', 'barrio']

    def __str__(self):
        return f'{self.ciudad} - {self.barrio or "Toda la ciudad"}'


class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')
    departamento = models.CharField(max_length=80)
    ciudad = models.CharField(max_length=80)
    barrio = models.CharField(max_length=80)
    direccion_completa = models.CharField(max_length=200)
    instrucciones = models.CharField(max_length=200, blank=True)
    telefono_contacto = models.CharField(max_length=20)
    es_principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'dirección'
        verbose_name_plural = 'direcciones'
        ordering = ['-es_principal', 'id']

    def __str__(self):
        return f'{self.direccion_completa}, {self.barrio}, {self.ciudad}'

    def save(self, *args, **kwargs):
        # Solo una dirección principal por cliente
        if self.es_principal:
            Direccion.objects.filter(cliente=self.cliente, es_principal=True).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)

    def _zona(self):
        zonas = ZonaDomicilio.objects.filter(activa=True, ciudad__iexact=self.ciudad)
        return zonas.filter(barrio__iexact=self.barrio).first() or zonas.filter(barrio='').first()

    def validar_cobertura(self):
        # Sin zonas configuradas se asume cobertura total
        if not ZonaDomicilio.objects.exists():
            return True
        return self._zona() is not None

    def obtener_costo_domicilio(self):
        from app_administracion.models import ConfiguracionTienda

        zona = self._zona()
        return zona.costo if zona else ConfiguracionTienda.obtener().costo_domicilio_base
