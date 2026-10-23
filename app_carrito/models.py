from django.db import models

from app_catalogo.models import Producto
from app_clientes.models import Cliente


class Carrito(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'carrito'
        verbose_name_plural = 'carritos'

    def __str__(self):
        return f'Carrito de {self.cliente}'

    def agregar_producto(self, producto, cantidad=1, talla='', color=''):
        item, creado = self.items.get_or_create(
            producto=producto, talla=talla, color=color, defaults={'cantidad': cantidad}
        )
        if not creado:
            item.cantidad += cantidad
            item.save()
        self.save()
        return item

    def eliminar_producto(self, id_item):
        self.items.filter(id=id_item).delete()
        self.save()

    def modificar_cantidad(self, id_item, cantidad):
        if cantidad <= 0:
            self.eliminar_producto(id_item)
        else:
            self.items.filter(id=id_item).update(cantidad=cantidad)
            self.save()

    def vaciar_carrito(self):
        self.items.all().delete()

    def obtener_items(self):
        return self.items.select_related('producto')

    def calcular_subtotal(self):
        return sum((item.subtotal for item in self.obtener_items()), 0)

    @property
    def cantidad_total(self):
        return sum(item.cantidad for item in self.items.all())


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    talla = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = 'ítem de carrito'
        verbose_name_plural = 'ítems de carrito'

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

    @property
    def subtotal(self):
        return self.producto.precio_venta * self.cantidad
