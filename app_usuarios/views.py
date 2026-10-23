from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from app_clientes.models import Cliente

from .forms import PerfilForm, RegistroForm


def _redireccion_por_rol(usuario):
    if usuario.es_admin:
        return 'administracion:dashboard'
    if usuario.rol == 'vendedor':
        return 'ventas:nueva'
    if usuario.rol == 'bodega':
        return 'inventario:lista'
    if usuario.es_repartidor:
        return 'domicilios:entregas'
    return 'catalogo:catalogo'


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect(_redireccion_por_rol(request.user))
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            if usuario.es_cliente:
                cliente, _ = Cliente.objects.get_or_create(usuario=usuario)
                cliente.visitas += 1
                cliente.save(update_fields=['visitas'])
            messages.success(request, f'Bienvenido, {usuario}.')
            return redirect(request.GET.get('next') or _redireccion_por_rol(usuario))
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'app_usuarios/login.html', {'form': form})


@require_POST
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('inicio:inicio')


def registrarse(request):
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save(commit=False)
        usuario.rol = 'cliente'
        usuario.save()
        Cliente.objects.create(usuario=usuario)
        login(request, usuario)
        messages.success(request, 'Tu cuenta fue creada. ¡Bienvenido a Dlune!')
        return redirect('catalogo:catalogo')
    return render(request, 'app_usuarios/registro.html', {'form': form})


@login_required
def perfil(request):
    form = PerfilForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado.')
        return redirect('usuarios:perfil')
    return render(request, 'app_usuarios/perfil.html', {'form': form})


@login_required
def cambiar_contrasena(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        update_session_auth_hash(request, usuario)
        messages.success(request, 'Contraseña actualizada.')
        return redirect('usuarios:perfil')
    return render(request, 'app_usuarios/cambiar_contrasena.html', {'form': form})
