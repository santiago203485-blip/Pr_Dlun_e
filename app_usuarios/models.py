from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario base del sistema. Administrador, Vendedor, Bodega, Repartidor y Cliente se distinguen por el rol."""

    ROL_ADMIN = 'admin'
    ROL_VENDEDOR = 'vendedor'
    ROL_BODEGA = 'bodega'
    ROL_REPARTIDOR = 'repartidor'
    ROL_CLIENTE = 'cliente'
    ROLES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_VENDEDOR, 'Vendedor'),
        (ROL_BODEGA, 'Auxiliar de bodega'),
        (ROL_REPARTIDOR, 'Repartidor'),
        (ROL_CLIENTE, 'Cliente'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default=ROL_CLIENTE)
    telefono = models.CharField(max_length=20, blank=True)
    foto = models.FileField(upload_to='usuarios/', blank=True, null=True)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN or self.is_superuser

    @property
    def es_personal(self):
        """Empleados de la tienda (todo menos cliente)."""
        return self.es_admin or self.rol in (self.ROL_VENDEDOR, self.ROL_BODEGA)

    @property
    def es_repartidor(self):
        return self.rol == self.ROL_REPARTIDOR

    @property
    def es_cliente(self):
        return self.rol == self.ROL_CLIENTE
