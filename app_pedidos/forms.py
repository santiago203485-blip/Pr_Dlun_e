from django import forms

from app_usuarios.models import Usuario

from .models import Pedido


class CheckoutForm(forms.Form):
    HORARIOS = [
        ('8:00 - 12:00', 'Mañana (8:00 - 12:00)'),
        ('12:00 - 16:00', 'Tarde (12:00 - 16:00)'),
        ('16:00 - 20:00', 'Noche (16:00 - 20:00)'),
    ]

    tipo_entrega = forms.ChoiceField(label='Tipo de entrega', choices=Pedido.TIPOS_ENTREGA, widget=forms.RadioSelect)
    direccion = forms.ModelChoiceField(label='Dirección de envío', queryset=None, required=False)
    horario_entrega = forms.ChoiceField(label='Horario de entrega', choices=HORARIOS)
    metodo_pago = forms.ChoiceField(label='Método de pago', choices=Pedido.METODOS_PAGO, widget=forms.RadioSelect)
    cupon = forms.CharField(label='Cupón de descuento', required=False, max_length=30)

    def __init__(self, cliente, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion'].queryset = cliente.direcciones.all()
        principal = cliente.direcciones.filter(es_principal=True).first()
        self.fields['direccion'].initial = principal
        self.fields['tipo_entrega'].initial = 'domicilio'
        self.fields['metodo_pago'].initial = 'tarjeta'

    def clean(self):
        datos = super().clean()
        if datos.get('tipo_entrega') == 'domicilio':
            direccion = datos.get('direccion')
            if not direccion:
                self.add_error('direccion', 'Selecciona una dirección para el domicilio.')
            elif not direccion.validar_cobertura():
                self.add_error('direccion', 'No hay cobertura de domicilio en esa dirección. Elige retiro en tienda.')
        if datos.get('tipo_entrega') == 'tienda' and datos.get('metodo_pago') == 'contra_entrega':
            self.add_error('metodo_pago', 'Contra entrega solo aplica para domicilios.')
        return datos


class CambiarEstadoForm(forms.Form):
    estado = forms.ChoiceField(label='Nuevo estado')
    comentario = forms.CharField(label='Comentario', required=False, max_length=200)

    def __init__(self, pedido, *args, **kwargs):
        super().__init__(*args, **kwargs)
        etiquetas = dict(Pedido.ESTADOS)
        self.fields['estado'].choices = [(e, etiquetas[e]) for e in Pedido.TRANSICIONES[pedido.estado]]


class AsignarRepartidorForm(forms.Form):
    repartidor = forms.ModelChoiceField(
        label='Repartidor', queryset=Usuario.objects.filter(rol='repartidor', is_active=True)
    )
