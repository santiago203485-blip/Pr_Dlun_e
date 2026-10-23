from django import forms

from .models import DisenoPersonalizado


class DisenoForm(forms.ModelForm):
    class Meta:
        model = DisenoPersonalizado
        fields = ('producto_base', 'descripcion', 'imagen_referencia', 'talla', 'color', 'cantidad')
        labels = {
            'producto_base': 'Pijama base (opcional)', 'descripcion': 'Descripción del estampado',
            'imagen_referencia': 'Imagen de referencia',
        }
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}


class RespuestaDisenoForm(forms.ModelForm):
    class Meta:
        model = DisenoPersonalizado
        fields = ('estado', 'precio_cotizado', 'respuesta_tienda')
        labels = {'respuesta_tienda': 'Mensaje para el cliente'}
        widgets = {'respuesta_tienda': forms.Textarea(attrs={'rows': 3})}
