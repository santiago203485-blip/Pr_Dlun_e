from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from app_catalogo.models import Producto
from app_pedidos.models import Pedido
from app_usuarios.models import Usuario
from app_ventas.models import Venta


class FlujoCompraTest(TestCase):
    """Recorre el diagrama de actividades: login -> catálogo -> carrito -> pedido -> pago."""

    @classmethod
    def setUpTestData(cls):
        call_command('datos_demo', verbosity=0)

    def test_compra_completa_con_reintento_de_pago(self):
        self.client.login(username='cliente', password='dlune1234')
        producto = Producto.objects.get(codigo='PJ-001')
        stock_inicial = producto.stock

        self.assertEqual(self.client.get(reverse('catalogo:catalogo'), {'genero': 'mujer'}).status_code, 200)
        self.client.post(reverse('carrito:agregar', args=[producto.pk]), {'talla': 'M', 'color': 'Azul', 'cantidad': 2})

        cliente = Usuario.objects.get(username='cliente').cliente
        respuesta = self.client.post(reverse('pedidos:checkout'), {
            'tipo_entrega': 'domicilio', 'direccion': cliente.direcciones.first().pk,
            'horario_entrega': '8:00 - 12:00', 'metodo_pago': 'tarjeta', 'cupon': 'DLUNE10',
        })
        pedido = Pedido.objects.get()
        self.assertRedirects(respuesta, reverse('pagos:pagar', args=[pedido.pk]))
        self.assertEqual(pedido.estado, Pedido.EN_PROCESO)
        self.assertGreater(pedido.descuento, 0)
        self.assertEqual(pedido.costo_domicilio, 8000)
        producto.refresh_from_db()
        self.assertEqual(producto.stock, stock_inicial - 2)

        # Pago rechazado -> reintentar -> aprobado
        self.client.post(reverse('pagos:pagar', args=[pedido.pk]), {'resultado': 'rechazar'})
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.EN_PROCESO)
        self.client.post(reverse('pagos:pagar', args=[pedido.pk]), {'resultado': 'aprobar'})
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.PAGADO)
        cliente.refresh_from_db()
        self.assertEqual(cliente.total_compras, 1)

        self.assertEqual(self.client.get(reverse('pedidos:detalle', args=[pedido.pk])).status_code, 200)

    def test_cancelar_pedido_devuelve_stock(self):
        self.client.login(username='cliente', password='dlune1234')
        producto = Producto.objects.get(codigo='PJ-003')
        self.client.post(reverse('carrito:agregar', args=[producto.pk]), {'talla': 'L', 'color': 'Rojo', 'cantidad': 1})
        self.client.post(reverse('pedidos:checkout'), {
            'tipo_entrega': 'tienda', 'horario_entrega': '8:00 - 12:00', 'metodo_pago': 'nequi',
        })
        pedido = Pedido.objects.get()
        self.client.post(reverse('pedidos:cancelar', args=[pedido.pk]))
        pedido.refresh_from_db()
        producto.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.CANCELADO)
        self.assertEqual(producto.stock, 15)


class VentaTiendaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('datos_demo', verbosity=0)

    def test_vendedor_registra_venta(self):
        self.client.login(username='vendedora', password='dlune1234')
        producto = Producto.objects.get(codigo='PJ-008')
        datos = {'metodo_pago': 'efectivo', 'items-TOTAL_FORMS': 5, 'items-INITIAL_FORMS': 0,
                 'items-0-producto': producto.pk, 'items-0-cantidad': 3}
        respuesta = self.client.post(reverse('ventas:nueva'), datos)
        venta = Venta.objects.get()
        self.assertRedirects(respuesta, reverse('ventas:factura', args=[venta.pk]))
        self.assertEqual(venta.subtotal, producto.precio_venta * 3)
        producto.refresh_from_db()
        self.assertEqual(producto.stock, 22)

    def test_permisos_por_rol(self):
        self.client.login(username='cliente', password='dlune1234')
        self.assertRedirects(self.client.get(reverse('administracion:dashboard')), reverse('inicio:inicio'))
        self.client.login(username='admin', password='dlune1234')
        for nombre in ['administracion:dashboard', 'reportes:reportes', 'inventario:lista', 'catalogo:productos',
                       'pedidos:gestion', 'clientes:lista', 'notificaciones:lista', 'administracion:usuarios',
                       'personalizacion:gestion', 'pagos:lista', 'domicilios:zonas', 'domicilios:entregas']:
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200, nombre)
