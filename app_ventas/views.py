from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from app_administracion.models import ConfiguracionTienda
from app_catalogo.models import Producto
from app_inventario.models import MovimientoInventario
from app_usuarios.decorators import rol_requerido

from .forms import DetalleVentaFormSet, VentaForm
from .models import DetalleVenta, Venta

personal_ventas = rol_requerido('admin', 'vendedor')


@personal_ventas
def lista_ventas(request):
    ventas = Venta.objects.select_related('vendedor', 'cliente__usuario')
    fecha = request.GET.get('fecha')
    if fecha:
        ventas = ventas.filter(fecha__date=fecha)
    if not request.user.es_admin:
        ventas = ventas.filter(vendedor=request.user)
    total = ventas.filter(estado=Venta.ACTIVA).aggregate(t=Sum('total'))['t'] or 0
    return render(request, 'app_ventas/lista.html', {'ventas': ventas, 'total': total, 'fecha': fecha})


@personal_ventas
def nueva_venta(request):
    form = VentaForm(request.POST or None)
    formset = DetalleVentaFormSet(request.POST or None, prefix='items')
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        lineas = [f.cleaned_data for f in formset if f.cleaned_data.get('producto') and f.cleaned_data.get('cantidad')]
        if not lineas:
            messages.error(request, 'Agrega al menos un producto.')
        else:
            venta = _registrar_venta(request, form, lineas)
            messages.success(request, f'Venta #{venta.id} registrada por ${venta.total:,.0f}.')
            return redirect('ventas:factura', pk=venta.pk)
    return render(request, 'app_ventas/nueva.html', {'form': form, 'formset': formset})


@transaction.atomic
def _registrar_venta(request, form, lineas):
    venta = form.save(commit=False)
    venta.vendedor = request.user
    venta.save()
    for linea in lineas:
        producto = linea['producto']
        DetalleVenta.objects.create(
            venta=venta, producto=producto, cantidad=linea['cantidad'], precio_unitario=producto.precio_venta
        )
        MovimientoInventario.registrar(producto, MovimientoInventario.SALIDA, linea['cantidad'], f'Venta #{venta.id}', request.user)
        Producto.objects.filter(pk=producto.pk).update(veces_vendido=F('veces_vendido') + linea['cantidad'])
    venta.calcular_total()
    if venta.cliente:
        venta.cliente.registrar_compra(venta.total)
    return venta


@personal_ventas
def factura(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'app_ventas/factura.html', {
        'venta': venta, 'config': ConfiguracionTienda.obtener(), 'ahora': timezone.now(),
    })


@rol_requerido('admin')
@require_POST
def anular_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if venta.anular(request.user):
        messages.success(request, f'Venta #{venta.id} anulada y stock devuelto.')
    else:
        messages.error(request, 'La venta ya estaba anulada.')
    return redirect('ventas:lista')
