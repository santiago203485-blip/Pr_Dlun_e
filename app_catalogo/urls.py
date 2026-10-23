from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle'),
    path('gestion/productos/', views.lista_productos, name='productos'),
    path('gestion/productos/nuevo/', views.producto_form, name='producto_nuevo'),
    path('gestion/productos/<int:pk>/editar/', views.producto_form, name='producto_editar'),
    path('gestion/productos/<int:pk>/eliminar/', views.eliminar_producto, name='producto_eliminar'),
    path('gestion/categorias/', views.lista_categorias, name='categorias'),
    path('gestion/categorias/nueva/', views.categoria_form, name='categoria_nueva'),
    path('gestion/categorias/<int:pk>/editar/', views.categoria_form, name='categoria_editar'),
    path('gestion/categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='categoria_eliminar'),
]
