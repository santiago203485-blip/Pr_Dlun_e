from django.urls import path

from . import views

app_name = 'pedidos'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/cancelar/', views.cancelar, name='cancelar'),
    path('gestion/', views.gestion_lista, name='gestion'),
    path('gestion/<int:pk>/', views.gestion_detalle, name='gestion_detalle'),
]
