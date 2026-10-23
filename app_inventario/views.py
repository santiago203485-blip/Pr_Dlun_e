from django.contrib import messages
from django.db.models import F
from django.shortcuts import redirect, render

from app_catalogo.models import Producto
from app_notificaciones.models import SolicitudStock
from app_usuarios.decorators import rol_requerido

from .forms import MovimientoForm
from .models import MovimientoInventario

gestion_inventario = rol_requerido('admin', 'bodega')


@gestion_inventario
def lista_inventario(request):
    productos = Producto.objects.select_related('categoria')
    if request.GET.get('bajo'):
        productos = productos.filter(stock__lte=F('stock_minimo'))
    contexto = {
        'productos': productos,
        'total_bajo': Producto.objects.filter(stock__lte=F('stock_minimo')).count(),
        'total_agotados': Producto.objects.filter(stock=0).count(),
    }
    return render(request, 'app_inventario/lista.html', contexto)


@gestion_inventario
def registrar_movimiento(request):
    form = MovimientoForm(request.POST or None, initial={'producto': request.GET.get('producto')})
    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        producto = datos['producto']
        estaba_agotado = producto.agotado
        MovimientoInventario.registrar(producto, datos['tipo'], datos['cantidad'], datos['motivo'], request.user)
        if estaba_agotado and not producto.agotado:
            avisados = SolicitudStock.avisar_disponibilidad(producto)
            if avisados:
                messages.info(request, f'Se avisó por WhatsApp a {avisados} cliente(s) que esperaban este producto.')
        if producto.esta_en_stock_bajo():
            messages.warning(request, f'Atención: "{producto.nombre}" está en stock bajo ({producto.stock} und).')
        messages.success(request, 'Movimiento registrado.')
        return redirect('inventario:lista')
    return render(request, 'app_inventario/movimiento_form.html', {'form': form})


@gestion_inventario
def historial_movimientos(request):
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario')[:200]
    return render(request, 'app_inventario/historial.html', {'movimientos': movimientos})
