from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_catalogo.forms import AgregarCarritoForm
from app_catalogo.models import Producto
from app_usuarios.decorators import cliente_requerido

from .models import Carrito


def _carrito(request):
    carrito, _ = Carrito.objects.get_or_create(cliente=request.user.cliente)
    return carrito


@cliente_requerido
def ver_carrito(request):
    carrito = _carrito(request)
    return render(request, 'app_carrito/carrito.html', {
        'carrito': carrito,
        'items': carrito.obtener_items(),
        'subtotal': carrito.calcular_subtotal(),
    })


@cliente_requerido
@require_POST
def agregar(request, pk):
    producto = get_object_or_404(Producto, pk=pk, visible=True)
    form = AgregarCarritoForm(producto, request.POST)
    if form.is_valid():
        datos = form.cleaned_data
        _carrito(request).agregar_producto(producto, datos['cantidad'], datos['talla'], datos['color'])
        messages.success(request, f'"{producto.nombre}" se agregó al carrito.')
        return redirect('carrito:ver')
    for errores in form.errors.values():
        messages.error(request, errores[0])
    return redirect('catalogo:detalle', pk=pk)


@cliente_requerido
@require_POST
def actualizar(request, item_id):
    carrito = _carrito(request)
    item = get_object_or_404(carrito.items, id=item_id)
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except ValueError:
        cantidad = item.cantidad
    if cantidad > item.producto.stock:
        messages.error(request, f'Solo hay {item.producto.stock} unidades de "{item.producto.nombre}".')
    else:
        carrito.modificar_cantidad(item_id, cantidad)
    return redirect('carrito:ver')


@cliente_requerido
@require_POST
def eliminar(request, item_id):
    _carrito(request).eliminar_producto(item_id)
    messages.info(request, 'Producto eliminado del carrito.')
    return redirect('carrito:ver')


@cliente_requerido
@require_POST
def vaciar(request):
    _carrito(request).vaciar_carrito()
    messages.info(request, 'Carrito vaciado.')
    return redirect('carrito:ver')
