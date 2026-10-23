from django.contrib import admin

from .models import DisenoPersonalizado


@admin.register(DisenoPersonalizado)
class DisenoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'precio_cotizado', 'fecha')
    list_filter = ('estado',)
