from django import forms

from .models import MovimientoInventario


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ('producto', 'tipo', 'cantidad', 'motivo')

    def clean(self):
        datos = super().clean()
        producto, tipo, cantidad = datos.get('producto'), datos.get('tipo'), datos.get('cantidad')
        if producto and tipo == MovimientoInventario.SALIDA and cantidad and cantidad > producto.stock:
            self.add_error('cantidad', f'Solo hay {producto.stock} unidades en stock.')
        if cantidad == 0:
            self.add_error('cantidad', 'La cantidad debe ser mayor a cero.')
        return datos
