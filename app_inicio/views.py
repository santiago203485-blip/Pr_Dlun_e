from app_catalogo.views import catalogo


def inicio(request):
    """La página de inicio muestra directamente el catálogo de pijamas."""
    return catalogo(request)
