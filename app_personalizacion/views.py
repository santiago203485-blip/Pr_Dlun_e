from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_notificaciones.models import Notificacion
from app_usuarios.decorators import cliente_requerido, rol_requerido

from .forms import DisenoForm, RespuestaDisenoForm
from .models import DisenoPersonalizado


@cliente_requerido
def mis_disenos(request):
    return render(request, 'app_personalizacion/mis_disenos.html', {
        'disenos': request.user.cliente.disenos.select_related('producto_base'),
    })


@cliente_requerido
def nuevo_diseno(request):
    form = DisenoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        diseno = form.save(commit=False)
        diseno.cliente = request.user.cliente
        diseno.save()
        messages.success(request, 'Recibimos tu diseño. Te enviaremos una cotización pronto.')
        return redirect('personalizacion:mis_disenos')
    return render(request, 'app_personalizacion/nuevo.html', {'form': form})


@cliente_requerido
@require_POST
def responder_cotizacion(request, pk):
    """El cliente acepta o rechaza la cotización."""
    diseno = get_object_or_404(DisenoPersonalizado, pk=pk, cliente=request.user.cliente, estado='cotizado')
    diseno.estado = 'aprobado' if request.POST.get('accion') == 'aceptar' else 'rechazado'
    diseno.save(update_fields=['estado'])
    messages.success(request, f'Diseño {diseno.get_estado_display().lower()}.')
    return redirect('personalizacion:mis_disenos')


@rol_requerido('admin', 'vendedor')
def gestion_disenos(request):
    disenos = DisenoPersonalizado.objects.select_related('cliente__usuario', 'producto_base')
    if request.GET.get('estado'):
        disenos = disenos.filter(estado=request.GET['estado'])
    return render(request, 'app_personalizacion/gestion.html', {
        'disenos': disenos, 'estados': DisenoPersonalizado.ESTADOS,
    })


@rol_requerido('admin', 'vendedor')
def gestion_detalle(request, pk):
    diseno = get_object_or_404(DisenoPersonalizado, pk=pk)
    form = RespuestaDisenoForm(request.POST or None, instance=diseno)
    if request.method == 'POST' and form.is_valid():
        diseno = form.save()
        Notificacion.enviar(diseno.cliente, Notificacion.TIPO_ESTADO,
                            f'Tu diseño personalizado #{diseno.id} está: {diseno.get_estado_display()}.')
        messages.success(request, 'Diseño actualizado y cliente notificado.')
        return redirect('personalizacion:gestion')
    return render(request, 'app_personalizacion/gestion_detalle.html', {'diseno': diseno, 'form': form})
