"""
URLs principales del proyecto Dlune.
Cada app tiene su propio archivo urls.py con su espacio de nombres.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_inicio.urls')),
    path('usuarios/', include('app_usuarios.urls')),
    path('catalogo/', include('app_catalogo.urls')),
    path('carrito/', include('app_carrito.urls')),
    path('pedidos/', include('app_pedidos.urls')),
    path('pagos/', include('app_pagos.urls')),
    path('domicilios/', include('app_domicilios.urls')),
    path('clientes/', include('app_clientes.urls')),
    path('inventario/', include('app_inventario.urls')),
    path('ventas/', include('app_ventas.urls')),
    path('notificaciones/', include('app_notificaciones.urls')),
    path('personalizacion/', include('app_personalizacion.urls')),
    path('reportes/', include('app_reportes.urls')),
    path('panel/', include('app_administracion.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
