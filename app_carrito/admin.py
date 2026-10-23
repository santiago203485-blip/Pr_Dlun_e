from django.contrib import admin

from .models import Carrito, ItemCarrito


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'ultima_actualizacion')
    inlines = [ItemCarritoInline]
