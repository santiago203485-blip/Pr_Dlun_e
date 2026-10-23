from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_usuarios.decorators import cliente_requerido, rol_requerido

from .models import Cliente


@rol_requerido('admin', 'vendedor')
def lista_clientes(request):
    clientes = Cliente.objects.select_related('usuario')
    q = request.GET.get('q', '').strip()
    if q:
        clientes = clientes.filter(
            Q(usuario__first_name__icontains=q) | Q(usuario__last_name__icontains=q)
            | Q(usuario__email__icontains=q) | Q(usuario__telefono__icontains=q)
        )
    if request.GET.get('vip'):
        clientes = clientes.filter(es_vip=True)
    return render(request, 'app_clientes/lista.html', {'clientes': clientes})


@rol_requerido('admin', 'vendedor')
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente.objects.select_related('usuario'), pk=pk)
    return render(request, 'app_clientes/detalle.html', {
        'cliente': cliente,
        'pedidos': cliente.pedidos.all()[:10],
        'ventas': cliente.ventas.all()[:10],
    })


@rol_requerido('admin')
@require_POST
def recalcular_vip(request):
    total = sum(1 for c in Cliente.objects.all() if c.actualizar_vip())
    messages.success(request, f'Clasificación actualizada: {total} clientes VIP.')
    return redirect('clientes:lista')


@cliente_requerido
@require_POST
def preferencias(request):
    cliente = request.user.cliente
    cliente.notificaciones_whatsapp = bool(request.POST.get('notificaciones_whatsapp'))
    cliente.save(update_fields=['notificaciones_whatsapp'])
    messages.success(request, 'Preferencias guardadas.')
    return redirect('usuarios:perfil')


@cliente_requerido
@require_POST
def eliminar_cuenta(request):
    """El cliente desactiva su cuenta (se conserva el historial de pedidos)."""
    from django.contrib.auth import logout

    usuario = request.user
    usuario.is_active = False
    usuario.save(update_fields=['is_active'])
    logout(request)
    messages.info(request, 'Tu cuenta fue eliminada. ¡Esperamos verte pronto!')
    return redirect('inicio:inicio')
