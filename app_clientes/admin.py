from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'total_compras', 'total_gastado', 'es_vip', 'fecha_registro')
    list_filter = ('es_vip',)
