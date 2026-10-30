def carrito(request):
    """Expone la cantidad del carrito y los mensajes sin leer del cliente en todas las plantillas."""
    usuario = getattr(request, 'user', None)
    datos = {'carrito_cantidad': 0, 'mensajes_sin_leer': 0}
    if usuario and usuario.is_authenticated and hasattr(usuario, 'cliente'):
        cliente = usuario.cliente
        carrito = getattr(cliente, 'carrito', None)
        if carrito:
            datos['carrito_cantidad'] = carrito.cantidad_total
        datos['mensajes_sin_leer'] = cliente.notificaciones.filter(leida=False).count()
    return datos
