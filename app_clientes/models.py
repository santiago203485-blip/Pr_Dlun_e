from django.conf import settings
from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    """Datos comerciales del cliente: historial de compras, VIP y preferencias."""

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cliente')
    fecha_registro = models.DateField(auto_now_add=True)
    total_compras = models.PositiveIntegerField(default=0)
    total_gastado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    es_vip = models.BooleanField(default=False)
    notificaciones_whatsapp = models.BooleanField(default=True)
    visitas = models.PositiveIntegerField(default=0)
    ultima_compra = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ['-total_gastado']

    def __str__(self):
        return str(self.usuario)

    @property
    def nombre(self):
        return str(self.usuario)

    @property
    def email(self):
        return self.usuario.email

    @property
    def telefono(self):
        return self.usuario.telefono

    def registrar_compra(self, monto):
        """Suma una compra al historial y recalcula si es VIP."""
        self.total_compras += 1
        self.total_gastado += monto
        self.ultima_compra = timezone.now()
        self.actualizar_vip(guardar=False)
        self.save()

    def actualizar_vip(self, guardar=True):
        """Clasifica al cliente como VIP según los criterios configurados por el administrador."""
        from app_administracion.models import ConfiguracionTienda

        config = ConfiguracionTienda.obtener()
        self.es_vip = (
            self.total_compras >= config.vip_min_compras
            or self.total_gastado >= config.vip_min_gastado
        )
        if guardar:
            self.save(update_fields=['es_vip'])
        return self.es_vip

    @property
    def dias_inactivo(self):
        if not self.ultima_compra:
            return None
        return (timezone.now() - self.ultima_compra).days
