import shutil
import tempfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from app_catalogo.models import Categoria, Producto
from app_notificaciones.models import Notificacion

MEDIA_PRUEBA = tempfile.mkdtemp()
# GIF de 1x1 píxel para probar la subida de imágenes
GIF = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00'
       b',\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')


@override_settings(MEDIA_ROOT=MEDIA_PRUEBA)
class PanelAdministradorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        with mock.patch.dict('os.environ', {'DEMO_PASSWORD': 'dlune1234'}):
            call_command('datos_demo', verbosity=0)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_PRUEBA, ignore_errors=True)

    def test_mensaje_a_todos_llega_a_la_bandeja_del_cliente(self):
        self.client.login(username='admin', password='dlune1234')
        respuesta = self.client.post(reverse('notificaciones:masivo'), {
            'segmento': 'todos', 'asunto': 'Nueva colección', 'mensaje': 'Hola {nombre}, llegaron pijamas nuevas.',
        })
        self.assertRedirects(respuesta, reverse('notificaciones:lista'))
        mensaje = Notificacion.objects.get(asunto='Nueva colección')
        self.assertIn('María López', mensaje.contenido)

        self.client.login(username='cliente', password='dlune1234')
        inicio = self.client.get(reverse('inicio:inicio'))
        self.assertEqual(inicio.context['mensajes_sin_leer'], 1)
        bandeja = self.client.get(reverse('notificaciones:mias'))
        self.assertContains(bandeja, 'Nueva colección')
        mensaje.refresh_from_db()
        self.assertTrue(mensaje.leida)

    def test_agregar_producto_con_imagen(self):
        self.client.login(username='admin', password='dlune1234')
        respuesta = self.client.post(reverse('catalogo:producto_nuevo'), {
            'codigo': 'PJ-100', 'nombre': 'Pijama Estrellas', 'descripcion': 'Algodón suave',
            'categoria': Categoria.objects.first().pk, 'genero': 'mujer', 'tallas': 'S,M', 'colores': 'Azul',
            'stock': 10, 'stock_minimo': 2, 'precio_compra': 40000, 'porcentaje_ganancia': 50, 'visible': 'on',
            'imagen': SimpleUploadedFile('pijama.gif', GIF, content_type='image/gif'),
        })
        self.assertRedirects(respuesta, reverse('catalogo:productos'))
        producto = Producto.objects.get(codigo='PJ-100')
        self.assertEqual(producto.precio_venta, 60000)
        self.assertTrue(producto.imagen.name.startswith('productos/'))
        self.assertContains(self.client.get(reverse('catalogo:catalogo')), producto.imagen.url)

    def test_rechaza_archivo_que_no_es_imagen(self):
        self.client.login(username='admin', password='dlune1234')
        respuesta = self.client.post(reverse('catalogo:producto_nuevo'), {
            'codigo': 'PJ-101', 'nombre': 'X', 'categoria': Categoria.objects.first().pk, 'genero': 'mujer',
            'tallas': 'M', 'colores': 'Azul', 'stock': 1, 'stock_minimo': 1, 'precio_compra': 1000,
            'porcentaje_ganancia': 10, 'imagen': SimpleUploadedFile('virus.exe', b'MZ', content_type='application/octet-stream'),
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Producto.objects.filter(codigo='PJ-101').exists())
