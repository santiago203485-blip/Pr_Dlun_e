from django.contrib import admin

from .models import MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'motivo', 'usuario', 'fecha')
    list_filter = ('tipo',)
