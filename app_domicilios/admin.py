from django.contrib import admin

from .models import Direccion, ZonaDomicilio

admin.site.register(ZonaDomicilio)


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'ciudad', 'barrio', 'direccion_completa', 'es_principal')
