from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_pedidos.models import Pedido
from app_usuarios.decorators import cliente_requerido, rol_requerido

from .forms import ComprobanteForm, CuponForm
from .models import Cupon, Pago


@cliente_requerido
def pagar(request, pedido_id):
    """Pasarela de pago simulada: el usuario elige si el banco aprueba o rechaza (para probar el reintento)."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, cliente=request.user.cliente)
    if pedido.estado != Pedido.EN_PROCESO:
        messages.info(request, 'Este pedido no tiene pagos pendientes.')
        return redirect('pedidos:detalle', pk=pedido.pk)

    form = ComprobanteForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        pago = Pago.objects.create(
            pedido=pedido, monto=pedido.total, metodo=pedido.metodo_pago,
            comprobante=form.cleaned_data.get('comprobante'),
        )
        aprobado = request.POST.get('resultado') == 'aprobar'
        if pago.procesar_pago(aprobado):
            messages.success(request, f'¡Pago aprobado! Transacción {pago.id_transaccion_externo}.')
            return redirect('pedidos:detalle', pk=pedido.pk)
        messages.error(request, f'Pago rechazado: {pago.motivo_rechazo}. Puedes reintentar.')
        return redirect('pagos:pagar', pedido_id=pedido.pk)

    return render(request, 'app_pagos/pagar.html', {
        'pedido': pedido, 'form': form, 'intentos': pedido.pagos.filter(estado=Pago.RECHAZADO),
    })


@rol_requerido('admin', 'vendedor')
def lista_pagos(request):
    pagos = Pago.objects.select_related('pedido__cliente__usuario')
    if request.GET.get('estado'):
        pagos = pagos.filter(estado=request.GET['estado'])
    return render(request, 'app_pagos/lista.html', {'pagos': pagos, 'estados': Pago.ESTADOS})


@rol_requerido('admin')
def cupones(request):
    form = CuponForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cupón creado.')
        return redirect('pagos:cupones')
    return render(request, 'app_pagos/cupones.html', {'form': form, 'cupones': Cupon.objects.all()})


@rol_requerido('admin')
@require_POST
def alternar_cupon(request, pk):
    cupon = get_object_or_404(Cupon, pk=pk)
    cupon.activo = not cupon.activo
    cupon.save(update_fields=['activo'])
    return redirect('pagos:cupones')
