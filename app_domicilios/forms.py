from django import forms

from .models import Direccion, ZonaDomicilio


class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ('departamento', 'ciudad', 'barrio', 'direccion_completa', 'instrucciones', 'telefono_contacto', 'es_principal')
        labels = {
            'direccion_completa': 'Dirección', 'telefono_contacto': 'Teléfono de contacto',
            'es_principal': 'Usar como dirección principal',
        }


class ZonaDomicilioForm(forms.ModelForm):
    class Meta:
        model = ZonaDomicilio
        fields = ('ciudad', 'barrio', 'costo', 'activa')
