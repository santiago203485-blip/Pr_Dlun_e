from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_carrito.models import Carrito
from app_inventario.models import MovimientoInventario
from app_notificaciones.models import Notificacion
from app_pagos.models import Pago
from app_usuarios.decorators import cliente_requerido, rol_requerido

from .forms import AsignarRepartidorForm, CambiarEstadoForm, CheckoutForm
from .models import DetallePedido, Pedido

gestion_pedidos = rol_requerido('admin', 'vendedor')


# ---------- Cliente ----------

@cliente_requerido
def checkout(request):
    cliente = request.user.cliente
    carrito, _ = Carrito.objects.get_or_create(cliente=cliente)
    items = list(carrito.obtener_items())
    if not items:
        messages.info(request, 'Tu carrito está vacío.')
        return redirect('catalogo:catalogo')

    form = CheckoutForm(cliente, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        sin_stock = [i.producto.nombre for i in items if i.cantidad > i.producto.stock]
        if sin_stock:
            messages.error(request, 'Sin stock suficiente para: ' + ', '.join(sin_stock))
            return redirect('carrito:ver')
        pedido = _crear_pedido(request, cliente, carrito, items, form.cleaned_data)
        if pedido.metodo_pago == 'contra_entrega':
            messages.success(request, f'Pedido #{pedido.id} confirmado. Pagas al recibirlo.')
            return redirect('pedidos:detalle', pk=pedido.pk)
        return redirect('pagos:pagar', pedido_id=pedido.pk)

    subtotal = carrito.calcular_subtotal()
    return render(request, 'app_pedidos/checkout.html', {'form': form, 'items': items, 'subtotal': subtotal})


@transaction.atomic
def _crear_pedido(request, cliente, carrito, items, datos):
    """Crea el pedido con sus detalles, descuenta inventario y vacía el carrito."""
    direccion = datos.get('direccion') if datos['tipo_entrega'] == 'domicilio' else None
    pedido = Pedido.objects.create(
        cliente=cliente,
        tipo_entrega=datos['tipo_entrega'],
        metodo_pago=datos['metodo_pago'],
        horario_entrega=datos['horario_entrega'],
        direccion_entrega=str(direccion) if direccion else 'Retiro en tienda',
        costo_domicilio=direccion.obtener_costo_domicilio() if direccion else 0,
    )
    for item in items:
        DetallePedido.objects.create(
            pedido=pedido, producto=item.producto, cantidad=item.cantidad,
            talla=item.talla, color=item.color, precio_unitario=item.producto.precio_venta,
        )
        MovimientoInventario.registrar(item.producto, MovimientoInventario.SALIDA, item.cantidad, f'Pedido #{pedido.id}')
        type(item.producto).objects.filter(pk=item.producto.pk).update(veces_vendido=F('veces_vendido') + item.cantidad)
    pedido.calcular_total()

    if datos.get('cupon'):
        if pedido.aplicar_cupon(datos['cupon']):
            messages.success(request, f'Cupón aplicado: -${pedido.descuento:,.0f}')
        else:
            messages.warning(request, 'El cupón no es válido.')

    pedido.historial.create(estado=Pedido.CREADO, usuario=request.user)
    pedido.cambiar_estado(Pedido.EN_PROCESO, request.user)
    Notificacion.enviar(cliente, Notificacion.TIPO_PEDIDO,
                        f'¡Gracias por tu compra! Recibimos tu pedido #{pedido.id} por ${pedido.total:,.0f}.')
    if pedido.metodo_pago == 'contra_entrega':
        Pago.objects.create(pedido=pedido, monto=pedido.total, metodo='contra_entrega')
        pedido.cambiar_estado(Pedido.PENDIENTE_PAGO, request.user)
    carrito.vaciar_carrito()
    return pedido


@cliente_requerido
def mis_pedidos(request):
    pedidos = request.user.cliente.pedidos.all()
    return render(request, 'app_pedidos/mis_pedidos.html', {'pedidos': pedidos})


@cliente_requerido
def detalle(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user.cliente)
    return render(request, 'app_pedidos/detalle.html', {'pedido': pedido})


@cliente_requerido
@require_POST
def cancelar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user.cliente)
    if pedido.estado == Pedido.ENVIADO:
        messages.error(request, 'El pedido ya fue enviado y no se puede cancelar.')
    elif pedido.cambiar_estado(Pedido.CANCELADO, request.user, 'Cancelado por el cliente'):
        messages.success(request, f'Pedido #{pedido.id} cancelado.')
    else:
        messages.error(request, 'Este pedido ya no se puede cancelar.')
    return redirect('pedidos:detalle', pk=pk)


# ---------- Gestión (admin / vendedor) ----------

@gestion_pedidos
def gestion_lista(request):
    pedidos = Pedido.objects.select_related('cliente__usuario', 'repartidor')
    estado = request.GET.get('estado')
    if estado:
        pedidos = pedidos.filter(estado=estado)
    return render(request, 'app_pedidos/gestion_lista.html', {
        'pedidos': pedidos, 'estados': Pedido.ESTADOS, 'estado_actual': estado,
    })


@gestion_pedidos
def gestion_detalle(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form_estado = CambiarEstadoForm(pedido)
    form_repartidor = AsignarRepartidorForm(initial={'repartidor': pedido.repartidor})

    if request.method == 'POST':
        if 'cambiar_estado' in request.POST:
            form_estado = CambiarEstadoForm(pedido, request.POST)
            if form_estado.is_valid():
                pedido.cambiar_estado(form_estado.cleaned_data['estado'], request.user, form_estado.cleaned_data['comentario'])
                messages.success(request, 'Estado actualizado y cliente notificado.')
                return redirect('pedidos:gestion_detalle', pk=pk)
        elif 'asignar_repartidor' in request.POST:
            form_repartidor = AsignarRepartidorForm(request.POST)
            if form_repartidor.is_valid():
                pedido.asignar_repartidor(form_repartidor.cleaned_data['repartidor'])
                messages.success(request, 'Repartidor asignado.')
                return redirect('pedidos:gestion_detalle', pk=pk)
        elif 'notas' in request.POST:
            pedido.notas_internas = request.POST.get('notas_internas', '')
            pedido.save(update_fields=['notas_internas'])
            messages.success(request, 'Notas guardadas.')
            return redirect('pedidos:gestion_detalle', pk=pk)

    return render(request, 'app_pedidos/gestion_detalle.html', {
        'pedido': pedido, 'form_estado': form_estado, 'form_repartidor': form_repartidor,
    })
