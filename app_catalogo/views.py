from django.contrib import messages
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_usuarios.decorators import rol_requerido

from .forms import AgregarCarritoForm, CategoriaForm, ProductoForm
from .models import Categoria, Producto

gestion_productos = rol_requerido('admin', 'bodega')


def _filtrar(productos, request):
    """Aplica búsqueda por texto y filtros de género/categoría."""
    q = request.GET.get('q', '').strip()
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(descripcion__icontains=q))
    if request.GET.get('genero'):
        productos = productos.filter(genero=request.GET['genero'])
    if request.GET.get('categoria'):
        productos = productos.filter(categoria_id=request.GET['categoria'])
    return productos


# ---------- Catálogo público ----------

def catalogo(request):
    productos = _filtrar(Producto.objects.filter(visible=True).select_related('categoria'), request)
    contexto = {
        'productos': productos,
        'categorias': Categoria.objects.filter(productos__visible=True).distinct(),
        'generos': Producto.GENEROS,
    }
    return render(request, 'app_catalogo/catalogo.html', contexto)


def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, visible=True)
    contexto = {
        'producto': producto,
        'form': AgregarCarritoForm(producto),
        'relacionados': Producto.objects.filter(categoria=producto.categoria, visible=True).exclude(pk=pk)[:4],
    }
    return render(request, 'app_catalogo/detalle.html', contexto)


# ---------- Gestión de productos (admin / bodega) ----------

@gestion_productos
def lista_productos(request):
    productos = _filtrar(Producto.objects.select_related('categoria'), request)
    return render(request, 'app_catalogo/productos_lista.html', {
        'productos': productos, 'categorias': Categoria.objects.all(),
    })


@gestion_productos
def producto_form(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if producto:
        form.fields['codigo'].disabled = True
    if request.method == 'POST' and form.is_valid():
        producto = form.save()
        messages.success(request, f'Producto "{producto.nombre}" guardado. Precio de venta: ${producto.precio_venta:,.0f}')
        return redirect('catalogo:productos')
    return render(request, 'app_catalogo/producto_form.html', {'form': form, 'producto': producto})


@gestion_productos
@require_POST
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    try:
        producto.delete()
        messages.success(request, 'Producto eliminado.')
    except ProtectedError:
        producto.visible = False
        producto.save(update_fields=['visible'])
        messages.warning(request, 'El producto tiene ventas o pedidos asociados: se ocultó del catálogo en lugar de eliminarse.')
    return redirect('catalogo:productos')


# ---------- Gestión de categorías (admin) ----------

@rol_requerido('admin')
def lista_categorias(request):
    categorias = Categoria.objects.annotate(total_productos=Count('productos'))
    q = request.GET.get('q', '').strip()
    if q:
        categorias = categorias.filter(nombre__icontains=q)
    return render(request, 'app_catalogo/categorias_lista.html', {'categorias': categorias})


@rol_requerido('admin')
def categoria_form(request, pk=None):
    categoria = get_object_or_404(Categoria, pk=pk) if pk else None
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría guardada.')
        return redirect('catalogo:categorias')
    return render(request, 'app_catalogo/categoria_form.html', {'form': form, 'categoria': categoria})


@rol_requerido('admin')
@require_POST
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if categoria.productos.exists():
        messages.error(request, 'No se puede eliminar: la categoría tiene productos asociados.')
    else:
        categoria.delete()
        messages.success(request, 'Categoría eliminada.')
    return redirect('catalogo:categorias')
