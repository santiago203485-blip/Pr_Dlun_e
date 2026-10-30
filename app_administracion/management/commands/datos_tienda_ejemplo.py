from django.core.management.base import BaseCommand

from app_administracion.models import ConfiguracionTienda

# Datos ficticios para presentar el prototipo. El teléfono y el correo no existen (dominio reservado .example).
# Se reemplazan desde Panel → Configuración → Tienda.
DATOS_EJEMPLO = {
    'nombre_tienda': 'Dlune Pijamas',
    'eslogan': 'Pijamas con estampados para toda la familia. Diseños propios y personalizados.',
    'nombre_responsable': 'Dlune Pijamas S.A.S.',
    'telefono_whatsapp': '300 000 0000',
    'telefono_fijo': '(604) 000 0000',
    'email_contacto': 'contacto@dlune.example',
    'direccion': 'Calle 10 # 40-20, Local 105',
    'ciudad': 'Medellín, Antioquia',
    'horario': 'Lunes a sábado de 9:00 a. m. a 7:00 p. m.',
}


class Command(BaseCommand):
    help = 'Llena los datos de contacto vacíos de la tienda con valores de ejemplo (no sobrescribe los que ya existen).'

    def add_arguments(self, parser):
        parser.add_argument('--sobrescribir', action='store_true', help='Reemplaza también los datos ya escritos.')

    def handle(self, *args, **opciones):
        config = ConfiguracionTienda.obtener()
        cambiados = []
        for campo, valor in DATOS_EJEMPLO.items():
            if opciones['sobrescribir'] or not getattr(config, campo):
                setattr(config, campo, valor)
                cambiados.append(campo)
        config.save()
        self.stdout.write(self.style.SUCCESS(f'Datos de la tienda actualizados: {", ".join(cambiados) or "ninguno"}.'))
