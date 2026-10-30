from django.shortcuts import render

from app_catalogo.models import Categoria, Producto


def inicio(request):
    contexto = {
        'destacados': Producto.objects.filter(visible=True, stock__gt=0).order_by('-veces_vendido')[:4],
        'nuevos': Producto.objects.filter(visible=True).order_by('-fecha_registro')[:4],
        'categorias': Categoria.objects.filter(productos__visible=True).distinct(),
    }
    return render(request, 'app_inicio/inicio.html', contexto)
