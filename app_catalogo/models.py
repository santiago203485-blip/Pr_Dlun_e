from decimal import Decimal

from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def obtener_productos(self):
        return self.productos.filter(visible=True)


class Producto(models.Model):
    GENERO_MUJER = 'mujer'
    GENERO_HOMBRE = 'hombre'
    GENERO_INFANTIL = 'infantil'
    GENEROS = [
        (GENERO_MUJER, 'Mujer'),
        (GENERO_HOMBRE, 'Hombre'),
        (GENERO_INFANTIL, 'Infantil'),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    genero = models.CharField(max_length=10, choices=GENEROS, default=GENERO_MUJER)
    tallas = models.CharField(max_length=100, default='S,M,L,XL', help_text='Separadas por coma')
    colores = models.CharField(max_length=150, default='Negro,Blanco', help_text='Separados por coma')
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=30)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    imagen = models.FileField(upload_to='productos/', blank=True, null=True)
    visible = models.BooleanField(default=True)
    veces_vendido = models.PositiveIntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.precio_venta = self.calcular_precio_venta()
        super().save(*args, **kwargs)

    def calcular_precio_venta(self):
        """Precio venta = precio compra x (1 + % ganancia / 100), redondeado a pesos."""
        factor = Decimal('1') + Decimal(self.porcentaje_ganancia) / Decimal('100')
        return (Decimal(self.precio_compra) * factor).quantize(Decimal('1'))

    def actualizar_stock(self, cantidad):
        """Suma (positivo) o resta (negativo) unidades sin bajar de cero."""
        self.stock = max(0, self.stock + cantidad)
        self.save(update_fields=['stock'])

    def esta_en_stock_bajo(self):
        return self.stock <= self.stock_minimo

    @property
    def agotado(self):
        return self.stock == 0

    def obtener_tallas_disponibles(self):
        return [t.strip() for t in self.tallas.split(',') if t.strip()]

    def obtener_colores_disponibles(self):
        return [c.strip() for c in self.colores.split(',') if c.strip()]
