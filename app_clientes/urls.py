from django.urls import path

from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.lista_clientes, name='lista'),
    path('<int:pk>/', views.detalle_cliente, name='detalle'),
    path('recalcular-vip/', views.recalcular_vip, name='recalcular_vip'),
    path('preferencias/', views.preferencias, name='preferencias'),
    path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
]
