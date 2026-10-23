from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def rol_requerido(*roles):
    """Permite el acceso solo a usuarios con alguno de los roles indicados (el superusuario siempre entra)."""

    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            usuario = request.user
            if usuario.is_superuser or usuario.rol in roles:
                return vista(request, *args, **kwargs)
            messages.error(request, 'Acceso denegado. No tienes permisos para esta sección.')
            return redirect('inicio:inicio')

        return envoltura

    return decorador


def cliente_requerido(vista):
    """Exige un usuario con perfil de cliente (lo crea si no existe)."""

    @wraps(vista)
    @login_required
    def envoltura(request, *args, **kwargs):
        from app_clientes.models import Cliente

        if not request.user.es_cliente:
            messages.error(request, 'Esta sección es solo para clientes.')
            return redirect('inicio:inicio')
        Cliente.objects.get_or_create(usuario=request.user)
        return vista(request, *args, **kwargs)

    return envoltura


solo_admin = rol_requerido('admin')
personal_tienda = rol_requerido('admin', 'vendedor', 'bodega')
