import os

from django.core.management.base import BaseCommand

from app_usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea el administrador inicial con ADMIN_USERNAME, ADMIN_EMAIL y ADMIN_PASSWORD (útil en hosts sin consola).'

    def handle(self, *args, **opciones):
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        if not username or not password:
            self.stdout.write('ADMIN_USERNAME o ADMIN_PASSWORD no definidos: no se crea administrador.')
            return
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(f'El usuario "{username}" ya existe.')
            return
        Usuario.objects.create_superuser(
            username=username, email=os.environ.get('ADMIN_EMAIL', ''), password=password,
            rol=Usuario.ROL_ADMIN, first_name='Administrador',
        )
        self.stdout.write(self.style.SUCCESS(f'Administrador "{username}" creado.'))
