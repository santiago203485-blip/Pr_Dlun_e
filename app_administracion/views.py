from datetime import date, timedelta

from django.contrib import messages
from django.db.models import F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_catalogo.models import Producto
from app_clientes.models import Cliente
from app_pedidos.models import Pedido
from app_usuarios.decorators import solo_admin
from app_usuarios.forms import UsuarioAdminForm
from app_usuarios.models import Usuario
from app_ventas.models import Venta

from .forms import ConfiguracionForm
from .models import ConfiguracionTienda


def _total(queryset):
    return queryset.aggregate(t=Sum('total'))['t'] or 0


@solo_admin
def dashboard(request):
    hoy = date.today()
    ventas = Venta.objects.filter(estado=Venta.ACTIVA)
    pedidos_pagados = Pedido.objects.filter(estado__in=[Pedido.PAGADO, Pedido.ENVIADO, Pedido.ENTREGADO])

    # Ventas de los últimos 7 días para la gráfica de barras
    semana = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        total = _total(ventas.filter(fecha__date=dia)) + _total(pedidos_pagados.filter(fecha__date=dia))
        semana.append({'dia': dia, 'total': total})
    maximo = max((d['total'] for d in semana), default=0) or 1
    for d in semana:
        d['porcentaje'] = int(d['total'] * 100 / maximo)

    contexto = {
        'ventas_hoy': _total(ventas.filter(fecha__date=hoy)) + _total(pedidos_pagados.filter(fecha__date=hoy)),
        'ventas_mes': _total(ventas.filter(fecha__year=hoy.year, fecha__month=hoy.month))
                      + _total(pedidos_pagados.filter(fecha__year=hoy.year, fecha__month=hoy.month)),
        'total_clientes': Cliente.objects.count(),
        'total_vip': Cliente.objects.filter(es_vip=True).count(),
        'pedidos_pendientes': Pedido.objects.filter(
            estado__in=[Pedido.CREADO, Pedido.EN_PROCESO, Pedido.PENDIENTE_PAGO, Pedido.PAGADO]
        ).count(),
        'ultimos_pedidos': Pedido.objects.select_related('cliente__usuario')[:5],
        'stock_bajo': Producto.objects.filter(stock__lte=F('stock_minimo')).order_by('stock')[:8],
        'semana': semana,
    }
    return render(request, 'app_administracion/dashboard.html', contexto)


# ---------- Gestión de usuarios del sistema ----------

@solo_admin
def lista_usuarios(request):
    usuarios = Usuario.objects.exclude(rol='cliente').order_by('rol', 'username')
    q = request.GET.get('q', '').strip()
    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(rol__icontains=q)
        )
    return render(request, 'app_administracion/usuarios_lista.html', {'usuarios': usuarios})


@solo_admin
def usuario_form(request, pk=None):
    usuario = get_object_or_404(Usuario, pk=pk) if pk else None
    form = UsuarioAdminForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario guardado.')
        return redirect('administracion:usuarios')
    return render(request, 'app_administracion/usuario_form.html', {'form': form, 'usuario_editado': usuario})


@solo_admin
@require_POST
def alternar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario.')
    else:
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
        messages.success(request, f'{usuario} ahora está {"activo" if usuario.is_active else "inactivo"}.')
    return redirect('administracion:usuarios')


@solo_admin
@require_POST
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
    elif usuario.ventas.exists():
        messages.error(request, 'El usuario tiene ventas registradas: desactívalo en lugar de eliminarlo.')
    else:
        usuario.delete()
        messages.success(request, 'Usuario eliminado.')
    return redirect('administracion:usuarios')


@solo_admin
def configuracion(request):
    form = ConfiguracionForm(request.POST or None, instance=ConfiguracionTienda.obtener())
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Configuración guardada.')
        return redirect('administracion:configuracion')
    return render(request, 'app_administracion/configuracion.html', {'form': form})
