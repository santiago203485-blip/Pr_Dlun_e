from django.db import models

from app_catalogo.models import Producto
from app_clientes.models import Cliente


class DisenoPersonalizado(models.Model):
    """Solicitud de una pijama con estampado personalizado."""

    ESTADOS = [
        ('solicitado', 'Solicitado'),
        ('cotizado', 'Cotizado'),
        ('aprobado', 'Aprobado'),
        ('en_produccion', 'En producción'),
        ('terminado', 'Terminado'),
        ('rechazado', 'Rechazado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='disenos')
    producto_base = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(help_text='Describe el estampado que quieres')
    imagen_referencia = models.FileField(upload_to='disenos/', blank=True, null=True)
    talla = models.CharField(max_length=10)
    color = models.CharField(max_length=30)
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='solicitado')
    precio_cotizado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    respuesta_tienda = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'diseño personalizado'
        verbose_name_plural = 'diseños personalizados'
        ordering = ['-fecha']

    def __str__(self):
        return f'Diseño #{self.id} de {self.cliente}'
