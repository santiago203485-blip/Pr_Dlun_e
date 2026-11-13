import os

from django.core.management.base import BaseCommand

from app_usuarios.models import Usuario


class Command(BaseCommand):
    help = ('Crea (o actualiza) el administrador con ADMIN_USERNAME, ADMIN_EMAIL y ADMIN_PASSWORD. '
            'Si el usuario ya existe, se le asigna la clave de ADMIN_PASSWORD y el rol de administrador.')

    def handle(self, *args, **opciones):
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        if not username or not password:
            self.stdout.write('ADMIN_USERNAME o ADMIN_PASSWORD no definidos: no se crea administrador.')
            return
        email = os.environ.get('ADMIN_EMAIL', '')
        usuario = Usuario.objects.filter(username=username).first()
        if usuario is None:
            Usuario.objects.create_superuser(
                username=username, email=email, password=password,
                rol=Usuario.ROL_ADMIN, first_name='Administrador',
            )
            self.stdout.write(self.style.SUCCESS(f'Administrador "{username}" creado.'))
            return
        # La variable de entorno manda: así se puede recuperar el acceso cambiando ADMIN_PASSWORD
        usuario.set_password(password)
        usuario.rol = Usuario.ROL_ADMIN
        usuario.is_staff = usuario.is_superuser = usuario.is_active = True
        if email:
            usuario.email = email
        usuario.save()
        self.stdout.write(self.style.SUCCESS(f'Administrador "{username}" actualizado.'))
