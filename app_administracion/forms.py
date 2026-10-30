from django import forms

from .models import ConfiguracionTienda


class ConfiguracionForm(forms.ModelForm):
    # Campos agrupados en la plantilla: datos de la tienda, contacto, redes y reglas del negocio
    GRUPOS = [
        ('Datos de la tienda', ['nombre_tienda', 'eslogan', 'nombre_responsable']),
        ('Contacto (se muestra en el pie de página)', ['telefono_whatsapp', 'telefono_fijo', 'email_contacto',
                                                       'direccion', 'ciudad', 'horario']),
        ('Redes sociales', ['instagram', 'facebook', 'tiktok']),
        ('Reglas del negocio', ['impuesto_porcentaje', 'costo_domicilio_base', 'vip_min_compras',
                                'vip_min_gastado', 'dias_cliente_inactivo']),
    ]

    class Meta:
        model = ConfiguracionTienda
        fields = '__all__'
        labels = {
            'nombre_tienda': 'Nombre de la tienda',
            'eslogan': 'Frase de la tienda',
            'nombre_responsable': 'Responsable',
            'telefono_whatsapp': 'WhatsApp',
            'telefono_fijo': 'Teléfono',
            'email_contacto': 'Correo de contacto',
            'direccion': 'Dirección de la tienda',
            'ciudad': 'Ciudad',
            'horario': 'Horario de atención',
            'instagram': 'Instagram',
            'facebook': 'Facebook',
            'tiktok': 'TikTok',
            'impuesto_porcentaje': 'Impuesto (%)',
            'costo_domicilio_base': 'Costo de domicilio base',
            'vip_min_compras': 'Compras mínimas para VIP',
            'vip_min_gastado': 'Monto mínimo para VIP',
            'dias_cliente_inactivo': 'Días sin comprar para considerar inactivo',
        }

    def grupos(self):
        return [(titulo, [self[campo] for campo in campos]) for titulo, campos in self.GRUPOS]
