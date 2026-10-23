from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_inventario, name='lista'),
    path('movimiento/', views.registrar_movimiento, name='movimiento'),
    path('historial/', views.historial_movimientos, name='historial'),
]
