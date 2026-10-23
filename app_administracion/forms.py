from django import forms

from .models import ConfiguracionTienda


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionTienda
        fields = '__all__'
        labels = {
            'nombre_tienda': 'Nombre de la tienda',
            'telefono_whatsapp': 'WhatsApp de la tienda',
            'impuesto_porcentaje': 'Impuesto (%)',
            'costo_domicilio_base': 'Costo de domicilio base',
            'vip_min_compras': 'Compras mínimas para VIP',
            'vip_min_gastado': 'Monto mínimo para VIP',
            'dias_cliente_inactivo': 'Días sin comprar para considerar inactivo',
        }
