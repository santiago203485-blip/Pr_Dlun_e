from .models import ConfiguracionTienda


def tienda(request):
    """Datos de la tienda (contacto, redes, horario) disponibles en todas las plantillas."""
    return {'tienda': ConfiguracionTienda.obtener()}
