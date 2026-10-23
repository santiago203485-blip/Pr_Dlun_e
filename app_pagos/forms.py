from django import forms

from .models import Cupon


class ComprobanteForm(forms.Form):
    """Para Nequi, Daviplata o transferencia el cliente puede adjuntar su comprobante."""

    comprobante = forms.FileField(label='Comprobante de pago (opcional)', required=False)


class CuponForm(forms.ModelForm):
    class Meta:
        model = Cupon
        fields = ('codigo', 'porcentaje', 'activo')
        labels = {'codigo': 'Código', 'porcentaje': '% de descuento'}
