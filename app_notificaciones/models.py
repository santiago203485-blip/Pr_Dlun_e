from django.db import models

from app_catalogo.models import Producto
from app_clientes.models import Cliente


class Notificacion(models.Model):
    """Mensaje para un cliente: se ve en su bandeja de la tienda y se registra para WhatsApp."""

    TIPO_PEDIDO = 'pedido'
    TIPO_ESTADO = 'estado'
    TIPO_CAMPANA = 'campana'
    TIPO_STOCK = 'stock'
    TIPOS = [
        (TIPO_PEDIDO, 'Confirmación de pedido'),
        (TIPO_ESTADO, 'Cambio de estado'),
        (TIPO_CAMPANA, 'Mensaje de la tienda'),
        (TIPO_STOCK, 'Producto disponible'),
    ]
    ENVIADO = 'enviado'
    OMITIDO = 'omitido'
    ESTADOS_ENVIO = [(ENVIADO, 'Enviado'), (OMITIDO, 'Omitido (cliente sin WhatsApp)')]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    asunto = models.CharField(max_length=120, blank=True)
    destinatario = models.CharField(max_length=20, blank=True)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado_envio = models.CharField(max_length=10, choices=ESTADOS_ENVIO, default=ENVIADO)
    leida = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'notificación'
        verbose_name_plural = 'notificaciones'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f'{self.get_tipo_display()} a {self.cliente}'

    @classmethod
    def enviar(cls, cliente, tipo, contenido, asunto=''):
        """Deja el mensaje en la bandeja del cliente. Aquí se conectaría la WhatsApp Business API."""
        puede = cliente.notificaciones_whatsapp and bool(cliente.telefono)
        return cls.objects.create(
            cliente=cliente, tipo=tipo, asunto=asunto, destinatario=cliente.telefono, contenido=contenido,
            estado_envio=cls.ENVIADO if puede else cls.OMITIDO,
        )

    @property
    def enlace_whatsapp(self):
        """Enlace wa.me para enviar el mensaje desde WhatsApp sin la API (números de Colombia)."""
        from urllib.parse import quote

        numero = ''.join(ch for ch in self.destinatario if ch.isdigit())
        if not numero:
            return ''
        if len(numero) == 10:
            numero = '57' + numero
        return f'https://wa.me/{numero}?text={quote(self.contenido)}'


class SolicitudStock(models.Model):
    """El cliente pide que le avisen cuando un producto agotado vuelva a estar disponible."""

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='solicitudes_stock')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='solicitudes_stock')
    fecha = models.DateTimeField(auto_now_add=True)
    atendida = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'solicitud de stock'
        verbose_name_plural = 'solicitudes de stock'

    def __str__(self):
        return f'{self.cliente} espera {self.producto}'

    @classmethod
    def avisar_disponibilidad(cls, producto):
        """Notifica a los clientes que esperaban el producto y marca sus solicitudes como atendidas."""
        pendientes = cls.objects.filter(producto=producto, atendida=False).select_related('cliente__usuario')
        for solicitud in pendientes:
            Notificacion.enviar(
                solicitud.cliente, Notificacion.TIPO_STOCK,
                f'¡Buenas noticias! La pijama "{producto.nombre}" ya está disponible en Dlune.',
            )
        return pendientes.update(atendida=True)
