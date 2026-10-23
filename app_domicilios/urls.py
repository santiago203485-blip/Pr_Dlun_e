from django.urls import path

from . import views

app_name = 'domicilios'

urlpatterns = [
    path('direcciones/', views.lista_direcciones, name='direcciones'),
    path('direcciones/nueva/', views.direccion_form, name='direccion_nueva'),
    path('direcciones/<int:pk>/editar/', views.direccion_form, name='direccion_editar'),
    path('direcciones/<int:pk>/eliminar/', views.eliminar_direccion, name='direccion_eliminar'),
    path('zonas/', views.zonas, name='zonas'),
    path('zonas/<int:pk>/eliminar/', views.eliminar_zona, name='zona_eliminar'),
    path('entregas/', views.entregas, name='entregas'),
    path('entregas/<int:pk>/estado/', views.actualizar_entrega, name='actualizar_entrega'),
]
