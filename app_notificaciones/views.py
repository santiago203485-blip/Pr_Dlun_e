from datetime import timedelta

from django import forms
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from app_administracion.models import ConfiguracionTienda
from app_catalogo.models import Producto
from app_clientes.models import Cliente
from app_usuarios.decorators import cliente_requerido, rol_requerido

from .models import Notificacion, SolicitudStock


class CampanaForm(forms.Form):
    SEGMENTOS = [
        ('todos', 'Todos los clientes'),
        ('vip', 'Solo clientes VIP'),
        ('inactivos', 'Clientes inactivos'),
    ]
    segmento = forms.ChoiceField(choices=SEGMENTOS)
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), max_length=1000,
                              help_text='Puedes usar {nombre} para personalizar el mensaje.')


def _clientes_segmento(segmento):
    clientes = Cliente.objects.filter(notificaciones_whatsapp=True, usuario__is_active=True).select_related('usuario')
    if segmento == 'vip':
        return clientes.filter(es_vip=True)
    if segmento == 'inactivos':
        limite = timezone.now() - timedelta(days=ConfiguracionTienda.obtener().dias_cliente_inactivo)
        return clientes.filter(Q(ultima_compra__lt=limite) | Q(ultima_compra__isnull=True))
    return clientes


@rol_requerido('admin')
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.select_related('cliente__usuario')[:200]
    return render(request, 'app_notificaciones/lista.html', {
        'notificaciones': notificaciones,
        'solicitudes': SolicitudStock.objects.filter(atendida=False).select_related('producto', 'cliente__usuario'),
    })


@rol_requerido('admin')
def whatsapp_masivo(request):
    form = CampanaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        clientes = _clientes_segmento(form.cleaned_data['segmento'])
        for cliente in clientes:
            texto = form.cleaned_data['mensaje'].replace('{nombre}', cliente.nombre)
            Notificacion.enviar(cliente, Notificacion.TIPO_CAMPANA, texto)
        messages.success(request, f'Campaña enviada a {clientes.count()} cliente(s).')
        return redirect('notificaciones:lista')
    return render(request, 'app_notificaciones/masivo.html', {'form': form})


@cliente_requerido
@require_POST
def solicitar_stock(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    SolicitudStock.objects.get_or_create(cliente=request.user.cliente, producto=producto, atendida=False)
    messages.success(request, 'Te avisaremos por WhatsApp cuando vuelva a estar disponible.')
    return redirect('catalogo:detalle', pk=producto_id)


@cliente_requerido
def mis_notificaciones(request):
    return render(request, 'app_notificaciones/mis_notificaciones.html', {
        'notificaciones': request.user.cliente.notificaciones.all()[:50],
    })
