from django import forms

from .models import Categoria, Producto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ('nombre', 'descripcion')
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = (
            'codigo', 'nombre', 'descripcion', 'categoria', 'genero', 'tallas', 'colores',
            'stock', 'stock_minimo', 'precio_compra', 'porcentaje_ganancia', 'imagen', 'visible',
        )
        labels = {
            'codigo': 'Código', 'descripcion': 'Descripción', 'categoria': 'Categoría',
            'genero': 'Género', 'stock_minimo': 'Stock mínimo de alerta',
            'porcentaje_ganancia': '% de ganancia', 'visible': 'Visible en catálogo',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tela, estampado, recomendaciones de lavado...'}),
            'imagen': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'tallas': forms.TextInput(attrs={'placeholder': 'S,M,L,XL'}),
            'colores': forms.TextInput(attrs={'placeholder': 'Negro,Blanco,Rosa'}),
        }


class AgregarCarritoForm(forms.Form):
    """Selección de talla, color y cantidad en el detalle del producto."""

    talla = forms.ChoiceField()
    color = forms.ChoiceField()
    cantidad = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, producto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producto = producto
        self.fields['talla'].choices = [(t, t) for t in producto.obtener_tallas_disponibles()]
        self.fields['color'].choices = [(c, c) for c in producto.obtener_colores_disponibles()]
        self.fields['cantidad'].max_value = producto.stock

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad > self.producto.stock:
            raise forms.ValidationError(f'Solo hay {self.producto.stock} unidades disponibles.')
        return cantidad
