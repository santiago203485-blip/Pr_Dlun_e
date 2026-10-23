from django.contrib import admin

from .models import DetalleVenta, Venta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'vendedor', 'cliente', 'total', 'metodo_pago', 'estado')
    list_filter = ('estado', 'metodo_pago')
    inlines = [DetalleVentaInline]
