from django.urls import path

from . import views

app_name = 'pagos'

urlpatterns = [
    path('pagar/<int:pedido_id>/', views.pagar, name='pagar'),
    path('', views.lista_pagos, name='lista'),
    path('cupones/', views.cupones, name='cupones'),
    path('cupones/<int:pk>/alternar/', views.alternar_cupon, name='cupon_alternar'),
]
