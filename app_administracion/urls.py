from django.urls import path

from . import views

app_name = 'administracion'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('usuarios/', views.lista_usuarios, name='usuarios'),
    path('usuarios/nuevo/', views.usuario_form, name='usuario_nuevo'),
    path('usuarios/<int:pk>/editar/', views.usuario_form, name='usuario_editar'),
    path('usuarios/<int:pk>/alternar/', views.alternar_usuario, name='usuario_alternar'),
    path('usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='usuario_eliminar'),
    path('configuracion/', views.configuracion, name='configuracion'),
]
