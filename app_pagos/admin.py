from django.contrib import admin

from .models import Cupon, Pago

admin.site.register(Cupon)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'monto', 'metodo', 'estado', 'fecha_transaccion')
    list_filter = ('estado', 'metodo')
