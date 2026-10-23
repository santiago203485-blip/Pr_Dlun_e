from django.contrib import admin

from .models import DetallePedido, HistorialEstado, Pedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


class HistorialEstadoInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total', 'estado', 'repartidor')
    list_filter = ('estado', 'tipo_entrega', 'metodo_pago')
    inlines = [DetallePedidoInline, HistorialEstadoInline]
