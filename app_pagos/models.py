import uuid

from django.db import models
from django.utils import timezone

from app_pedidos.models import Pedido


class Cupon(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, help_text='% de descuento')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'cupón'
        verbose_name_plural = 'cupones'

    def __str__(self):
        return f'{self.codigo} ({self.porcentaje}%)'


class Pago(models.Model):
    PENDIENTE = 'pendiente'
    APROBADO = 'aprobado'
    RECHAZADO = 'rechazado'
    ESTADOS = [(PENDIENTE, 'Pendiente'), (APROBADO, 'Aprobado'), (RECHAZADO, 'Rechazado')]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=Pedido.METODOS_PAGO)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    fecha_transaccion = models.DateTimeField(null=True, blank=True)
    id_transaccion_externo = models.CharField(max_length=60, blank=True)
    motivo_rechazo = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'pago'
        verbose_name_plural = 'pagos'
        ordering = ['-id']

    def __str__(self):
        return f'Pago {self.id} - {self.pedido} ({self.get_estado_display()})'

    def procesar_pago(self, aprobado=True, motivo=''):
        """Simula la respuesta de la pasarela de pago (Wompi/PayU) y actualiza el pedido."""
        self.fecha_transaccion = timezone.now()
        self.id_transaccion_externo = uuid.uuid4().hex[:16].upper()
        if aprobado:
            self.verificar_pago()
        else:
            self.rechazar_pago(motivo or 'Fondos insuficientes')
        return self.estado == self.APROBADO

    def verificar_pago(self):
        self.estado = self.APROBADO
        self.save()
        self.pedido.cambiar_estado(Pedido.PAGADO, comentario=f'Pago {self.id_transaccion_externo} aprobado')
        self.pedido.cliente.registrar_compra(self.monto)
        return True

    def rechazar_pago(self, motivo):
        self.estado = self.RECHAZADO
        self.motivo_rechazo = motivo
        self.save()
