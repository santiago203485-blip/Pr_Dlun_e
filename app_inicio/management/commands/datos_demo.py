import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from app_administracion.models import ConfiguracionTienda
from app_clientes.models import Cliente
from app_domicilios.models import Direccion, ZonaDomicilio
from app_pagos.models import Cupon
from app_usuarios.models import Usuario

# Contraseña de todos los usuarios de prueba (solo para desarrollo)
CLAVE_DEMO = 'dlune1234'

USUARIOS = [
    ('admin', 'Laura', 'Gómez', 'admin'),
    ('vendedora', 'Camila', 'Ruiz', 'vendedor'),
    ('bodega', 'Andrés', 'Pérez', 'bodega'),
    ('repartidor', 'Jhon', 'Martínez', 'repartidor'),
    ('cliente', 'María', 'López', 'cliente'),
]



class Command(BaseCommand):
    help = 'Crea usuarios de prueba, zonas, cupón y el catálogo inicial de Dlune.'

    def handle(self, *args, **opciones):
        ConfiguracionTienda.obtener()

        # En producción no se crean usuarios con la clave conocida: se exige DEMO_PASSWORD
        clave = os.environ.get('DEMO_PASSWORD') or (CLAVE_DEMO if settings.DEBUG else None)
        if clave:
            self.crear_usuarios(clave)
            self.stdout.write(f'Usuarios de prueba: {", ".join(u[0] for u in USUARIOS)}')
        else:
            self.stdout.write('DEBUG=False y sin DEMO_PASSWORD: se cargan productos sin usuarios de prueba.')
        self.crear_catalogo()

    def crear_usuarios(self, clave):
        for username, nombre, apellido, rol in USUARIOS:
            usuario, creado = Usuario.objects.get_or_create(
                username=username,
                defaults={'first_name': nombre, 'last_name': apellido, 'rol': rol,
                          'email': f'{username}@dlune.test', 'telefono': '3001234567'},
            )
            if creado:
                usuario.set_password(clave)
                usuario.is_staff = usuario.is_superuser = rol == 'admin'
                usuario.save()

        cliente, _ = Cliente.objects.get_or_create(usuario=Usuario.objects.get(username='cliente'))
        if not cliente.direcciones.exists():
            Direccion.objects.create(
                cliente=cliente, departamento='Antioquia', ciudad='Medellín', barrio='Laureles',
                direccion_completa='Calle 10 # 70-20', telefono_contacto='3001234567', es_principal=True,
            )

    def crear_catalogo(self):
        ZonaDomicilio.objects.get_or_create(ciudad='Medellín', barrio='', defaults={'costo': 8000})
        ZonaDomicilio.objects.get_or_create(ciudad='Envigado', barrio='', defaults={'costo': 10000})
        Cupon.objects.get_or_create(codigo='DLUNE10', defaults={'porcentaje': 10})

        call_command('cargar_catalogo', verbosity=0, stdout=self.stdout)

        self.stdout.write(self.style.SUCCESS('Datos de prueba listos.'))
