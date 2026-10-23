from django.core.management.base import BaseCommand

from app_administracion.models import ConfiguracionTienda
from app_catalogo.models import Categoria, Producto
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

PRODUCTOS = [
    ('PJ-001', 'Pijama Luna Estrellada', 'Navideña', 'mujer', 45000, 'Azul,Negro'),
    ('PJ-002', 'Pijama Ositos Polares', 'Invierno', 'infantil', 30000, 'Blanco,Rosa'),
    ('PJ-003', 'Pijama Clásica Cuadros', 'Invierno', 'hombre', 50000, 'Rojo,Gris'),
    ('PJ-004', 'Short Tropical', 'Verano', 'mujer', 28000, 'Verde,Amarillo'),
    ('PJ-005', 'Pijama Dinosaurios', 'Estampados animales', 'infantil', 32000, 'Verde,Azul'),
    ('PJ-006', 'Pijama Gatitos', 'Estampados animales', 'mujer', 42000, 'Rosa,Lila'),
    ('PJ-007', 'Pijama Renos', 'Navideña', 'hombre', 48000, 'Rojo,Verde'),
    ('PJ-008', 'Bermuda Palmeras', 'Verano', 'hombre', 26000, 'Azul,Blanco'),
]


class Command(BaseCommand):
    help = 'Crea usuarios, categorías, productos y cupones de prueba para Dlune.'

    def handle(self, *args, **opciones):
        ConfiguracionTienda.obtener()

        for username, nombre, apellido, rol in USUARIOS:
            usuario, creado = Usuario.objects.get_or_create(
                username=username,
                defaults={'first_name': nombre, 'last_name': apellido, 'rol': rol,
                          'email': f'{username}@dlune.test', 'telefono': '3001234567'},
            )
            if creado:
                usuario.set_password(CLAVE_DEMO)
                usuario.is_staff = usuario.is_superuser = rol == 'admin'
                usuario.save()

        cliente, _ = Cliente.objects.get_or_create(usuario=Usuario.objects.get(username='cliente'))
        if not cliente.direcciones.exists():
            Direccion.objects.create(
                cliente=cliente, departamento='Antioquia', ciudad='Medellín', barrio='Laureles',
                direccion_completa='Calle 10 # 70-20', telefono_contacto='3001234567', es_principal=True,
            )

        ZonaDomicilio.objects.get_or_create(ciudad='Medellín', barrio='', defaults={'costo': 8000})
        ZonaDomicilio.objects.get_or_create(ciudad='Envigado', barrio='', defaults={'costo': 10000})
        Cupon.objects.get_or_create(codigo='DLUNE10', defaults={'porcentaje': 10})

        for i, (codigo, nombre, categoria, genero, precio, colores) in enumerate(PRODUCTOS):
            cat, _ = Categoria.objects.get_or_create(nombre=categoria)
            Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre, 'categoria': cat, 'genero': genero, 'precio_compra': precio,
                    'porcentaje_ganancia': 60, 'colores': colores, 'stock': [20, 3, 15, 0, 12, 8, 4, 25][i],
                    'descripcion': f'{nombre} en algodón suave, ideal para dormir cómodo.',
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Datos de prueba listos. Usuarios: {", ".join(u[0] for u in USUARIOS)} (contraseña: {CLAVE_DEMO})'
        ))
