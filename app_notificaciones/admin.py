from django.contrib import admin

from .models import Notificacion, SolicitudStock


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'estado_envio', 'fecha_envio')
    list_filter = ('tipo', 'estado_envio')


admin.site.register(SolicitudStock)
