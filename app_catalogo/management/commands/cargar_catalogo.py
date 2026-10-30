from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from app_catalogo.catalogo_inicial import CATEGORIAS, CUIDADO, PRODUCTOS
from app_catalogo.models import Categoria, Producto

IMAGENES = Path(__file__).resolve().parents[2] / 'imagenes_catalogo'


class Command(BaseCommand):
    help = 'Carga el catálogo inicial de pijamas Dlune con sus fotos (no duplica productos existentes).'

    def add_arguments(self, parser):
        parser.add_argument('--ocultar-anteriores', action='store_true',
                            help='Oculta del catálogo los productos que no pertenecen a este catálogo (no los borra).')
        parser.add_argument('--actualizar', action='store_true',
                            help='Actualiza nombre, descripción, colores, categoría y foto de los productos que ya existen '
                                 '(no cambia stock ni precios).')

    def handle(self, *args, **opciones):
        for nombre, descripcion in CATEGORIAS.items():
            Categoria.objects.get_or_create(nombre=nombre, defaults={'descripcion': descripcion})

        creados = actualizados = 0
        for codigo, nombre, categoria, genero, compra, tallas, colores, stock, descripcion, _ in PRODUCTOS:
            datos = {
                'nombre': nombre, 'categoria': Categoria.objects.get(nombre=categoria), 'genero': genero,
                'tallas': tallas, 'colores': colores, 'descripcion': f'{descripcion}\n\nCuidado: {CUIDADO}',
            }
            producto, nuevo = Producto.objects.get_or_create(codigo=codigo, defaults={
                **datos, 'precio_compra': compra, 'porcentaje_ganancia': 60, 'stock': stock, 'stock_minimo': 5,
            })
            creados += nuevo
            if not nuevo and opciones['actualizar']:
                for campo, valor in datos.items():
                    setattr(producto, campo, valor)
                producto.save()
                actualizados += 1
            imagen = IMAGENES / f'{codigo.lower()}.jpg'
            if imagen.exists() and (not producto.imagen or (opciones['actualizar'] and not nuevo)):
                with imagen.open('rb') as archivo:
                    producto.imagen.save(imagen.name, File(archivo), save=True)

        if opciones['ocultar_anteriores']:
            codigos = [p[0] for p in PRODUCTOS]
            ocultos = Producto.objects.exclude(codigo__in=codigos).filter(visible=True).update(visible=False)
            self.stdout.write(f'Productos anteriores ocultos: {ocultos}')
        self.stdout.write(self.style.SUCCESS(
            f'Catálogo listo: {creados} nuevos y {actualizados} actualizados de {len(PRODUCTOS)}.'
        ))
