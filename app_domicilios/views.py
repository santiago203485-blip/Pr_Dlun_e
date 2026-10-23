from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_pagos.models import Pago
from app_pedidos.models import Pedido
from app_usuarios.decorators import cliente_requerido, rol_requerido

from .forms import DireccionForm, ZonaDomicilioForm
from .models import Direccion, ZonaDomicilio


# ---------- Direcciones del cliente ----------

@cliente_requerido
def lista_direcciones(request):
    direcciones = request.user.cliente.direcciones.all()
    return render(request, 'app_domicilios/direcciones.html', {'direcciones': direcciones})


@cliente_requerido
def direccion_form(request, pk=None):
    cliente = request.user.cliente
    direccion = get_object_or_404(Direccion, pk=pk, cliente=cliente) if pk else None
    form = DireccionForm(request.POST or None, instance=direccion,
                         initial={'telefono_contacto': request.user.telefono})
    if request.method == 'POST' and form.is_valid():
        direccion = form.save(commit=False)
        direccion.cliente = cliente
        if not cliente.direcciones.exists():
            direccion.es_principal = True
        direccion.save()
        if not direccion.validar_cobertura():
            messages.warning(request, 'Por ahora no tenemos cobertura de domicilio en esa zona. Puedes retirar en tienda.')
        else:
            messages.success(request, 'Dirección guardada.')
        return redirect(request.GET.get('next') or 'domicilios:direcciones')
    return render(request, 'app_domicilios/direccion_form.html', {'form': form, 'direccion': direccion})


@cliente_requerido
@require_POST
def eliminar_direccion(request, pk):
    get_object_or_404(Direccion, pk=pk, cliente=request.user.cliente).delete()
    messages.info(request, 'Dirección eliminada.')
    return redirect('domicilios:direcciones')


# ---------- Zonas de cobertura (admin) ----------

@rol_requerido('admin')
def zonas(request):
    form = ZonaDomicilioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Zona agregada.')
        return redirect('domicilios:zonas')
    return render(request, 'app_domicilios/zonas.html', {'form': form, 'zonas': ZonaDomicilio.objects.all()})


@rol_requerido('admin')
@require_POST
def eliminar_zona(request, pk):
    get_object_or_404(ZonaDomicilio, pk=pk).delete()
    return redirect('domicilios:zonas')


# ---------- Entregas del repartidor ----------

@rol_requerido('repartidor', 'admin')
def entregas(request):
    pedidos = Pedido.objects.filter(tipo_entrega='domicilio').select_related('cliente__usuario')
    if not request.user.es_admin:
        pedidos = pedidos.filter(repartidor=request.user)
    return render(request, 'app_domicilios/entregas.html', {
        'activos': pedidos.filter(estado__in=[Pedido.PAGADO, Pedido.PENDIENTE_PAGO, Pedido.ENVIADO]),
        'entregados': pedidos.filter(estado=Pedido.ENTREGADO)[:20],
    })


@rol_requerido('repartidor', 'admin')
@require_POST
def actualizar_entrega(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if not request.user.es_admin and pedido.repartidor != request.user:
        messages.error(request, 'Este pedido no está asignado a ti.')
        return redirect('domicilios:entregas')
    nuevo_estado = request.POST.get('estado')
    comentario = request.POST.get('comentario', '')
    if pedido.cambiar_estado(nuevo_estado, request.user, comentario):
        # El pago contra entrega se confirma cuando el repartidor entrega el pedido
        if nuevo_estado == Pedido.ENTREGADO and pedido.metodo_pago == 'contra_entrega':
            pago = pedido.pagos.filter(estado=Pago.PENDIENTE).first()
            if pago:
                pago.estado = Pago.APROBADO
                pago.save()
                pedido.cliente.registrar_compra(pago.monto)
        messages.success(request, f'Pedido #{pedido.id} actualizado a "{pedido.get_estado_display()}".')
    else:
        messages.error(request, 'Cambio de estado no permitido.')
    return redirect('domicilios:entregas')
