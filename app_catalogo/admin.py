from django.contrib import admin

from .models import Categoria, Producto

admin.site.register(Categoria)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'genero', 'stock', 'precio_venta', 'visible')
    list_filter = ('categoria', 'genero', 'visible')
    search_fields = ('codigo', 'nombre')
