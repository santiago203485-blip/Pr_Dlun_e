import csv
from datetime import date, timedelta

from django.db.models import Count, F, Q, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from app_administracion.models import ConfiguracionTienda
from app_catalogo.models import Producto
from app_clientes.models import Cliente
from app_pedidos.models import Pedido
from app_usuarios.decorators import rol_requerido
from app_ventas.models import Venta


def _rango(request):
    """Rango de fechas del filtro (por defecto, últimos 30 días)."""
    hoy = date.today()
    try:
        desde = date.fromisoformat(request.GET.get('desde', ''))
    except ValueError:
        desde = hoy - timedelta(days=30)
    try:
        hasta = date.fromisoformat(request.GET.get('hasta', ''))
    except ValueError:
        hasta = hoy
    return desde, hasta


def _datos(desde, hasta):
    ventas = Venta.objects.filter(estado=Venta.ACTIVA, fecha__date__range=(desde, hasta))
    pedidos = Pedido.objects.filter(
        fecha__date__range=(desde, hasta), estado__in=[Pedido.PAGADO, Pedido.ENVIADO, Pedido.ENTREGADO]
    )
    limite_inactivo = timezone.now() - timedelta(days=ConfiguracionTienda.obtener().dias_cliente_inactivo)
    return {
        'ventas': ventas.select_related('vendedor', 'cliente__usuario'),
        'total_tienda': ventas.aggregate(t=Sum('total'))['t'] or 0,
        'total_online': pedidos.aggregate(t=Sum('total'))['t'] or 0,
        'num_ventas': ventas.count(),
        'num_pedidos': pedidos.count(),
        'top_productos': Producto.objects.filter(veces_vendido__gt=0).order_by('-veces_vendido')[:10],
        'stock_bajo': Producto.objects.filter(stock__lte=F('stock_minimo')).order_by('stock'),
        'mejores_clientes': Cliente.objects.select_related('usuario').filter(total_gastado__gt=0)[:10],
        'inactivos': Cliente.objects.select_related('usuario').filter(
            Q(ultima_compra__lt=limite_inactivo) | Q(ultima_compra__isnull=True)
        ),
        'por_metodo': ventas.values('metodo_pago').annotate(n=Count('id'), t=Sum('total')).order_by('-t'),
    }


@rol_requerido('admin')
def reportes(request):
    desde, hasta = _rango(request)
    contexto = _datos(desde, hasta)
    contexto.update({'desde': desde, 'hasta': hasta})
    contexto['total_general'] = contexto['total_tienda'] + contexto['total_online']
    return render(request, 'app_reportes/reportes.html', contexto)


@rol_requerido('admin')
def exportar(request, tipo):
    """Exporta el reporte a CSV (se abre directamente en Excel)."""
    desde, hasta = _rango(request)
    datos = _datos(desde, hasta)
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="reporte_{tipo}_{desde}_{hasta}.csv"'
    respuesta.write('﻿')  # BOM para que Excel respete las tildes
    escritor = csv.writer(respuesta, delimiter=';')

    if tipo == 'ventas':
        escritor.writerow(['ID', 'Fecha', 'Vendedor', 'Cliente', 'Método', 'Subtotal', 'Impuesto', 'Total'])
        for v in datos['ventas']:
            escritor.writerow([v.id, v.fecha.strftime('%Y-%m-%d %H:%M'), v.vendedor, v.cliente or 'Mostrador',
                               v.get_metodo_pago_display(), v.subtotal, v.impuesto, v.total])
    elif tipo == 'productos':
        escritor.writerow(['Código', 'Producto', 'Unidades vendidas', 'Stock'])
        for p in datos['top_productos']:
            escritor.writerow([p.codigo, p.nombre, p.veces_vendido, p.stock])
    elif tipo == 'inventario':
        escritor.writerow(['Código', 'Producto', 'Stock', 'Stock mínimo'])
        for p in datos['stock_bajo']:
            escritor.writerow([p.codigo, p.nombre, p.stock, p.stock_minimo])
    elif tipo == 'inactivos':
        escritor.writerow(['Cliente', 'Correo', 'Teléfono', 'Última compra', 'Total gastado'])
        for c in datos['inactivos']:
            escritor.writerow([c.nombre, c.email, c.telefono,
                               c.ultima_compra.strftime('%Y-%m-%d') if c.ultima_compra else 'Nunca', c.total_gastado])
    else:
        raise Http404('Reporte no existe')
    return respuesta
