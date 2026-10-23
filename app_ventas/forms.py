from django import forms

from app_catalogo.models import Producto
from app_clientes.models import Cliente

from .models import Venta


class VentaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.select_related('usuario'), required=False,
        empty_label='Cliente de mostrador (sin registrar)',
    )

    class Meta:
        model = Venta
        fields = ('cliente', 'metodo_pago')
        labels = {'metodo_pago': 'Método de pago'}


class DetalleVentaForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.filter(stock__gt=0), required=False)
    cantidad = forms.IntegerField(min_value=1, initial=1, required=False)

    def clean(self):
        datos = super().clean()
        producto, cantidad = datos.get('producto'), datos.get('cantidad')
        if producto and cantidad and cantidad > producto.stock:
            self.add_error('cantidad', f'Solo hay {producto.stock} und de {producto.nombre}.')
        return datos


DetalleVentaFormSet = forms.formset_factory(DetalleVentaForm, extra=5)
