from decimal import Decimal

from django.conf import settings
from django.db import models

from app_catalogo.models import Producto
from app_clientes.models import Cliente


class Pedido(models.Model):
    # Estados según el diagrama de estados
    CREADO = 'creado'
    EN_PROCESO = 'en_proceso'
    PENDIENTE_PAGO = 'pendiente_pago'
    PAGADO = 'pagado'
    ENVIADO = 'enviado'
    ENTREGADO = 'entregado'
    CANCELADO = 'cancelado'
    ESTADOS = [
        (CREADO, 'Creado'),
        (EN_PROCESO, 'En proceso'),
        (PENDIENTE_PAGO, 'Pendiente de pago'),
        (PAGADO, 'Pagado'),
        (ENVIADO, 'Enviado'),
        (ENTREGADO, 'Entregado'),
        (CANCELADO, 'Cancelado'),
    ]
    TRANSICIONES = {
        CREADO: [EN_PROCESO, CANCELADO],
        EN_PROCESO: [PENDIENTE_PAGO, PAGADO, CANCELADO],
        PENDIENTE_PAGO: [ENVIADO, CANCELADO],
        PAGADO: [ENVIADO, CANCELADO],
        ENVIADO: [ENTREGADO, CANCELADO],
        ENTREGADO: [],
        CANCELADO: [],
    }

    METODOS_PAGO = [
        ('tarjeta', 'Tarjeta débito/crédito'),
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
        ('transferencia', 'Transferencia'),
        ('contra_entrega', 'Contra entrega'),
    ]
    TIPOS_ENTREGA = [('domicilio', 'Domicilio'), ('tienda', 'Retiro en tienda')]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='entregas', limit_choices_to={'rol': 'repartidor'},
    )
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_domicilio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=CREADO)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='tarjeta')
    tipo_entrega = models.CharField(max_length=10, choices=TIPOS_ENTREGA, default='domicilio')
    direccion_entrega = models.CharField(max_length=250, blank=True)
    horario_entrega = models.CharField(max_length=50, blank=True)
    cupon = models.CharField(max_length=30, blank=True)
    notas_internas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'
        ordering = ['-fecha']

    def __str__(self):
        return f'Pedido #{self.id}'

    def calcular_total(self):
        """Recalcula subtotal, impuesto y total a partir de los detalles."""
        from app_administracion.models import ConfiguracionTienda

        self.subtotal = sum((d.subtotal for d in self.detalles.all()), Decimal('0'))
        self.impuesto = ConfiguracionTienda.obtener().calcular_impuesto(self.subtotal - self.descuento)
        self.total = self.subtotal - self.descuento + self.impuesto + self.costo_domicilio
        self.save()
        return self.total

    def puede_cambiar_a(self, nuevo_estado):
        return nuevo_estado in self.TRANSICIONES.get(self.estado, [])

    def cambiar_estado(self, nuevo_estado, usuario=None, comentario=''):
        """Cambia el estado si la transición es válida, guarda el historial y notifica al cliente."""
        if not self.puede_cambiar_a(nuevo_estado):
            return False
        if nuevo_estado == self.CANCELADO:
            self._devolver_stock()
        self.estado = nuevo_estado
        self.save(update_fields=['estado'])
        HistorialEstado.objects.create(pedido=self, estado=nuevo_estado, usuario=usuario, comentario=comentario)

        from app_notificaciones.models import Notificacion

        Notificacion.enviar(
            self.cliente, Notificacion.TIPO_ESTADO,
            f'Hola {self.cliente.nombre}, tu pedido #{self.id} ahora está: {self.get_estado_display()}.',
        )
        return True

    def asignar_repartidor(self, repartidor):
        self.repartidor = repartidor
        self.save(update_fields=['repartidor'])

    def aplicar_cupon(self, codigo):
        """Aplica un cupón válido y devuelve el descuento (0 si no es válido)."""
        from app_pagos.models import Cupon

        cupon = Cupon.objects.filter(codigo__iexact=codigo, activo=True).first()
        if not cupon:
            return Decimal('0')
        self.cupon = cupon.codigo
        self.descuento = (self.subtotal * cupon.porcentaje / Decimal('100')).quantize(Decimal('1'))
        self.calcular_total()
        return self.descuento

    def obtener_historial_estados(self):
        return self.historial.all()

    def _devolver_stock(self):
        from app_inventario.models import MovimientoInventario

        for detalle in self.detalles.select_related('producto'):
            MovimientoInventario.registrar(
                detalle.producto, MovimientoInventario.ENTRADA, detalle.cantidad, f'Cancelación pedido #{self.id}'
            )

    @property
    def esta_activo(self):
        return self.estado not in (self.ENTREGADO, self.CANCELADO)


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    talla = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=30, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'detalle de pedido'
        verbose_name_plural = 'detalles de pedido'

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

    def save(self, *args, **kwargs):
        self.subtotal = self.calcular_subtotal()
        super().save(*args, **kwargs)

    def calcular_subtotal(self):
        return self.precio_unitario * self.cantidad


class HistorialEstado(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historial')
    estado = models.CharField(max_length=20, choices=Pedido.ESTADOS)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    comentario = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'historial de estado'
        verbose_name_plural = 'historial de estados'
        ordering = ['fecha']

    def __str__(self):
        return f'{self.pedido} -> {self.get_estado_display()}'
