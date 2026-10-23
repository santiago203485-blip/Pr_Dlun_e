def carrito(request):
    """Expone la cantidad de productos del carrito en todas las plantillas."""
    usuario = getattr(request, 'user', None)
    if usuario and usuario.is_authenticated and hasattr(usuario, 'cliente'):
        carrito = getattr(usuario.cliente, 'carrito', None)
        if carrito:
            return {'carrito_cantidad': carrito.cantidad_total}
    return {'carrito_cantidad': 0}
