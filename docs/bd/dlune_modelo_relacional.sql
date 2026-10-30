-- =====================================================================
-- Modelo relacional del sistema Dlune (tienda de pijamas con estampados)
-- Motor: MySQL 8.0  ·  Para MySQL Workbench:
--   File > Import > Reverse Engineer MySQL Create Script...
-- Convención (igual al diagrama de clases): cada palabra en mayúscula
-- y unidas con "_". Las llaves primarias son Id_<Tabla>.
-- Equivale a los modelos Django del proyecto (una tabla por modelo).
-- =====================================================================

DROP SCHEMA IF EXISTS Dlune;
CREATE SCHEMA Dlune DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE Dlune;

-- ---------------------------------------------------------------------
-- Usuarios y clientes
-- ---------------------------------------------------------------------
CREATE TABLE Usuario (
  Id_Usuario      INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Usuario         VARCHAR(150) NOT NULL,
  Nombres         VARCHAR(150) NOT NULL DEFAULT '',
  Apellidos       VARCHAR(150) NOT NULL DEFAULT '',
  Email           VARCHAR(254) NOT NULL DEFAULT '',
  Contrasena      VARCHAR(128) NOT NULL COMMENT 'Hash PBKDF2, nunca texto plano',
  Telefono        VARCHAR(20)  NOT NULL DEFAULT '',
  Foto            VARCHAR(100) NULL COMMENT 'Ruta del archivo en media/usuarios/',
  Rol             ENUM('Admin','Vendedor','Bodega','Repartidor','Cliente') NOT NULL DEFAULT 'Cliente',
  Activo          TINYINT(1)   NOT NULL DEFAULT 1,
  Es_Superusuario TINYINT(1)   NOT NULL DEFAULT 0,
  Ultimo_Acceso   DATETIME     NULL,
  Fecha_Registro  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (Id_Usuario),
  UNIQUE KEY Uq_Usuario_Usuario (Usuario),
  KEY Ix_Usuario_Rol (Rol)
) ENGINE=InnoDB COMMENT='Personas que ingresan al sistema; el Rol define Administrador, Vendedor, Auxiliar de bodega, Repartidor o Cliente';

CREATE TABLE Cliente (
  Id_Cliente              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Usuario              INT UNSIGNED NOT NULL,
  Fecha_Registro          DATE          NOT NULL,
  Total_Compras           INT UNSIGNED  NOT NULL DEFAULT 0,
  Total_Gastado           DECIMAL(12,2) NOT NULL DEFAULT 0,
  Es_Vip                  TINYINT(1)    NOT NULL DEFAULT 0,
  Notificaciones_Whatsapp TINYINT(1)    NOT NULL DEFAULT 1,
  Visitas                 INT UNSIGNED  NOT NULL DEFAULT 0,
  Ultima_Compra           DATETIME      NULL,
  PRIMARY KEY (Id_Cliente),
  UNIQUE KEY Uq_Cliente_Usuario (Id_Usuario),
  KEY Ix_Cliente_Vip (Es_Vip),
  CONSTRAINT Fk_Cliente_Usuario FOREIGN KEY (Id_Usuario) REFERENCES Usuario (Id_Usuario)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Datos comerciales del usuario con rol Cliente (relación 1 a 1)';

CREATE TABLE Configuracion_Tienda (
  Id_Configuracion      INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Nombre_Tienda         VARCHAR(100)  NOT NULL DEFAULT 'Dlune Pijamas',
  Telefono_Whatsapp     VARCHAR(20)   NOT NULL DEFAULT '',
  Impuesto_Porcentaje   DECIMAL(5,2)  NOT NULL DEFAULT 19.00,
  Costo_Domicilio_Base  DECIMAL(10,2) NOT NULL DEFAULT 8000.00,
  Vip_Min_Compras       INT UNSIGNED  NOT NULL DEFAULT 5,
  Vip_Min_Gastado       DECIMAL(12,2) NOT NULL DEFAULT 500000.00,
  Dias_Cliente_Inactivo INT UNSIGNED  NOT NULL DEFAULT 60,
  PRIMARY KEY (Id_Configuracion)
) ENGINE=InnoDB COMMENT='Parámetros de la tienda (registro único)';

-- ---------------------------------------------------------------------
-- Catálogo e inventario
-- ---------------------------------------------------------------------
CREATE TABLE Categoria (
  Id_Categoria INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Nombre       VARCHAR(80) NOT NULL,
  Descripcion  TEXT        NULL,
  PRIMARY KEY (Id_Categoria),
  UNIQUE KEY Uq_Categoria_Nombre (Nombre)
) ENGINE=InnoDB;

CREATE TABLE Producto (
  Id_Producto         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Codigo              VARCHAR(30)   NOT NULL,
  Nombre              VARCHAR(120)  NOT NULL,
  Descripcion         TEXT          NULL,
  Id_Categoria        INT UNSIGNED  NOT NULL,
  Genero              ENUM('Mujer','Hombre','Infantil') NOT NULL DEFAULT 'Mujer',
  Tallas              VARCHAR(100)  NOT NULL DEFAULT 'S,M,L,XL',
  Colores             VARCHAR(150)  NOT NULL DEFAULT 'Negro,Blanco',
  Stock               INT UNSIGNED  NOT NULL DEFAULT 0,
  Stock_Minimo        INT UNSIGNED  NOT NULL DEFAULT 5,
  Precio_Compra       DECIMAL(10,2) NOT NULL,
  Porcentaje_Ganancia DECIMAL(5,2)  NOT NULL DEFAULT 30.00,
  Precio_Venta        DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Precio_Compra * (1 + Porcentaje_Ganancia / 100)',
  Imagen              VARCHAR(100)  NULL COMMENT 'Ruta en media/productos/ (jpg, png, webp, gif)',
  Visible             TINYINT(1)    NOT NULL DEFAULT 1,
  Veces_Vendido       INT UNSIGNED  NOT NULL DEFAULT 0,
  Fecha_Registro      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (Id_Producto),
  UNIQUE KEY Uq_Producto_Codigo (Codigo),
  KEY Ix_Producto_Categoria (Id_Categoria),
  KEY Ix_Producto_Genero (Genero),
  CONSTRAINT Fk_Producto_Categoria FOREIGN KEY (Id_Categoria) REFERENCES Categoria (Id_Categoria)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT Ck_Producto_Precio CHECK (Precio_Compra >= 0 AND Porcentaje_Ganancia >= 0)
) ENGINE=InnoDB;

CREATE TABLE Movimiento_Inventario (
  Id_Movimiento INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Producto   INT UNSIGNED NOT NULL,
  Id_Usuario    INT UNSIGNED NULL COMMENT 'Quién registró el movimiento (NULL = Sistema)',
  Tipo          ENUM('Entrada','Salida') NOT NULL,
  Cantidad      INT UNSIGNED NOT NULL,
  Motivo        VARCHAR(150) NOT NULL DEFAULT '',
  Fecha         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (Id_Movimiento),
  KEY Ix_Movimiento_Producto (Id_Producto),
  KEY Ix_Movimiento_Usuario (Id_Usuario),
  CONSTRAINT Fk_Movimiento_Producto FOREIGN KEY (Id_Producto) REFERENCES Producto (Id_Producto)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Fk_Movimiento_Usuario FOREIGN KEY (Id_Usuario) REFERENCES Usuario (Id_Usuario)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT Ck_Movimiento_Cantidad CHECK (Cantidad > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Carrito
-- ---------------------------------------------------------------------
CREATE TABLE Carrito (
  Id_Carrito           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Cliente           INT UNSIGNED NOT NULL,
  Fecha_Creacion       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Ultima_Actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (Id_Carrito),
  UNIQUE KEY Uq_Carrito_Cliente (Id_Cliente),
  CONSTRAINT Fk_Carrito_Cliente FOREIGN KEY (Id_Cliente) REFERENCES Cliente (Id_Cliente)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Item_Carrito (
  Id_Item     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Carrito  INT UNSIGNED NOT NULL,
  Id_Producto INT UNSIGNED NOT NULL,
  Cantidad    INT UNSIGNED NOT NULL DEFAULT 1,
  Talla       VARCHAR(10) NOT NULL DEFAULT '',
  Color       VARCHAR(30) NOT NULL DEFAULT '',
  PRIMARY KEY (Id_Item),
  KEY Ix_Item_Carrito (Id_Carrito),
  KEY Ix_Item_Producto (Id_Producto),
  CONSTRAINT Fk_Item_Carrito FOREIGN KEY (Id_Carrito) REFERENCES Carrito (Id_Carrito)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Fk_Item_Producto FOREIGN KEY (Id_Producto) REFERENCES Producto (Id_Producto)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Domicilios
-- ---------------------------------------------------------------------
CREATE TABLE Zona_Domicilio (
  Id_Zona INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Ciudad  VARCHAR(80)   NOT NULL,
  Barrio  VARCHAR(80)   NOT NULL DEFAULT '' COMMENT 'Vacío = toda la ciudad',
  Costo   DECIMAL(10,2) NOT NULL,
  Activa  TINYINT(1)    NOT NULL DEFAULT 1,
  PRIMARY KEY (Id_Zona),
  KEY Ix_Zona_Ciudad (Ciudad, Barrio)
) ENGINE=InnoDB;

CREATE TABLE Direccion (
  Id_Direccion       INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Cliente         INT UNSIGNED NOT NULL,
  Departamento       VARCHAR(80)  NOT NULL,
  Ciudad             VARCHAR(80)  NOT NULL,
  Barrio             VARCHAR(80)  NOT NULL,
  Direccion_Completa VARCHAR(200) NOT NULL,
  Instrucciones      VARCHAR(200) NOT NULL DEFAULT '',
  Telefono_Contacto  VARCHAR(20)  NOT NULL,
  Es_Principal       TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (Id_Direccion),
  KEY Ix_Direccion_Cliente (Id_Cliente),
  CONSTRAINT Fk_Direccion_Cliente FOREIGN KEY (Id_Cliente) REFERENCES Cliente (Id_Cliente)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Pedidos y pagos
-- ---------------------------------------------------------------------
CREATE TABLE Cupon (
  Id_Cupon   INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Codigo     VARCHAR(30)  NOT NULL,
  Porcentaje DECIMAL(5,2) NOT NULL,
  Activo     TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (Id_Cupon),
  UNIQUE KEY Uq_Cupon_Codigo (Codigo),
  CONSTRAINT Ck_Cupon_Porcentaje CHECK (Porcentaje > 0 AND Porcentaje <= 100)
) ENGINE=InnoDB;

CREATE TABLE Pedido (
  Id_Pedido         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Cliente        INT UNSIGNED NOT NULL,
  Id_Repartidor     INT UNSIGNED NULL COMMENT 'Usuario con Rol = Repartidor',
  Id_Cupon          INT UNSIGNED NULL,
  Fecha             DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Subtotal          DECIMAL(12,2) NOT NULL DEFAULT 0,
  Costo_Domicilio   DECIMAL(10,2) NOT NULL DEFAULT 0,
  Impuesto          DECIMAL(10,2) NOT NULL DEFAULT 0,
  Descuento         DECIMAL(10,2) NOT NULL DEFAULT 0,
  Total             DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT 'Subtotal - Descuento + Impuesto + Costo_Domicilio',
  Estado            ENUM('Creado','En_Proceso','Pendiente_Pago','Pagado','Enviado','Entregado','Cancelado') NOT NULL DEFAULT 'Creado',
  Metodo_Pago       ENUM('Tarjeta','Nequi','Daviplata','Transferencia','Contra_Entrega') NOT NULL DEFAULT 'Tarjeta',
  Tipo_Entrega      ENUM('Domicilio','Retiro_Tienda') NOT NULL DEFAULT 'Domicilio',
  Direccion_Entrega VARCHAR(250) NOT NULL DEFAULT '' COMMENT 'Copia de la dirección al momento del pedido',
  Horario_Entrega   VARCHAR(50)  NOT NULL DEFAULT '',
  Notas_Internas    TEXT         NULL,
  PRIMARY KEY (Id_Pedido),
  KEY Ix_Pedido_Cliente (Id_Cliente),
  KEY Ix_Pedido_Repartidor (Id_Repartidor),
  KEY Ix_Pedido_Cupon (Id_Cupon),
  KEY Ix_Pedido_Estado (Estado),
  KEY Ix_Pedido_Fecha (Fecha),
  CONSTRAINT Fk_Pedido_Cliente FOREIGN KEY (Id_Cliente) REFERENCES Cliente (Id_Cliente)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT Fk_Pedido_Repartidor FOREIGN KEY (Id_Repartidor) REFERENCES Usuario (Id_Usuario)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT Fk_Pedido_Cupon FOREIGN KEY (Id_Cupon) REFERENCES Cupon (Id_Cupon)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Detalle_Pedido (
  Id_Detalle      INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Pedido       INT UNSIGNED NOT NULL,
  Id_Producto     INT UNSIGNED NOT NULL,
  Cantidad        INT UNSIGNED  NOT NULL,
  Talla           VARCHAR(10)   NOT NULL DEFAULT '',
  Color           VARCHAR(30)   NOT NULL DEFAULT '',
  Precio_Unitario DECIMAL(10,2) NOT NULL COMMENT 'Precio de venta al momento de la compra',
  Subtotal        DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT 'Precio_Unitario * Cantidad',
  PRIMARY KEY (Id_Detalle),
  KEY Ix_Detalle_Pedido (Id_Pedido),
  KEY Ix_Detalle_Producto (Id_Producto),
  CONSTRAINT Fk_Detalle_Pedido FOREIGN KEY (Id_Pedido) REFERENCES Pedido (Id_Pedido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Fk_Detalle_Producto FOREIGN KEY (Id_Producto) REFERENCES Producto (Id_Producto)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT Ck_Detalle_Cantidad CHECK (Cantidad > 0)
) ENGINE=InnoDB;

CREATE TABLE Historial_Estado (
  Id_Historial INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Pedido    INT UNSIGNED NOT NULL,
  Id_Usuario   INT UNSIGNED NULL COMMENT 'Quién cambió el estado (NULL = Sistema)',
  Estado       ENUM('Creado','En_Proceso','Pendiente_Pago','Pagado','Enviado','Entregado','Cancelado') NOT NULL,
  Fecha        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Comentario   VARCHAR(200) NOT NULL DEFAULT '',
  PRIMARY KEY (Id_Historial),
  KEY Ix_Historial_Pedido (Id_Pedido),
  KEY Ix_Historial_Usuario (Id_Usuario),
  CONSTRAINT Fk_Historial_Pedido FOREIGN KEY (Id_Pedido) REFERENCES Pedido (Id_Pedido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Fk_Historial_Usuario FOREIGN KEY (Id_Usuario) REFERENCES Usuario (Id_Usuario)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Pago (
  Id_Pago                INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Pedido              INT UNSIGNED NOT NULL,
  Monto                  DECIMAL(12,2) NOT NULL,
  Metodo                 ENUM('Tarjeta','Nequi','Daviplata','Transferencia','Contra_Entrega') NOT NULL,
  Estado                 ENUM('Pendiente','Aprobado','Rechazado') NOT NULL DEFAULT 'Pendiente',
  Comprobante            VARCHAR(100) NULL COMMENT 'Ruta en media/comprobantes/',
  Fecha_Transaccion      DATETIME     NULL,
  Id_Transaccion_Externo VARCHAR(60)  NOT NULL DEFAULT '' COMMENT 'Referencia de la pasarela de pago',
  Motivo_Rechazo         VARCHAR(200) NOT NULL DEFAULT '',
  PRIMARY KEY (Id_Pago),
  KEY Ix_Pago_Pedido (Id_Pedido),
  KEY Ix_Pago_Estado (Estado),
  CONSTRAINT Fk_Pago_Pedido FOREIGN KEY (Id_Pedido) REFERENCES Pedido (Id_Pedido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Ventas en tienda
-- ---------------------------------------------------------------------
CREATE TABLE Venta (
  Id_Venta    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Vendedor INT UNSIGNED NOT NULL COMMENT 'Usuario con Rol = Vendedor o Admin',
  Id_Cliente  INT UNSIGNED NULL COMMENT 'NULL = cliente de mostrador',
  Fecha       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Subtotal    DECIMAL(12,2) NOT NULL DEFAULT 0,
  Impuesto    DECIMAL(10,2) NOT NULL DEFAULT 0,
  Total       DECIMAL(12,2) NOT NULL DEFAULT 0,
  Metodo_Pago ENUM('Efectivo','Tarjeta','Nequi','Daviplata','Transferencia') NOT NULL DEFAULT 'Efectivo',
  Estado      ENUM('Activa','Anulada') NOT NULL DEFAULT 'Activa',
  PRIMARY KEY (Id_Venta),
  KEY Ix_Venta_Vendedor (Id_Vendedor),
  KEY Ix_Venta_Cliente (Id_Cliente),
  KEY Ix_Venta_Fecha (Fecha),
  CONSTRAINT Fk_Venta_Vendedor FOREIGN KEY (Id_Vendedor) REFERENCES Usuario (Id_Usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT Fk_Venta_Cliente FOREIGN KEY (Id_Cliente) REFERENCES Cliente (Id_Cliente)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Detalle_Venta (
  Id_Detalle_Venta INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Venta         INT UNSIGNED NOT NULL,
  Id_Producto      INT UNSIGNED NOT NULL,
  Cantidad         INT UNSIGNED  NOT NULL,
  Precio_Unitario  DECIMAL(10,2) NOT NULL,
  Subtotal         DECIMAL(12,2) NOT NULL DEFAULT 0,
  PRIMARY KEY (Id_Detalle_Venta),
  KEY Ix_Detalle_Venta_Venta (Id_Venta),
  KEY Ix_Detalle_Venta_Producto (Id_Producto),
  CONSTRAINT Fk_Detalle_Venta_Venta FOREIGN KEY (Id_Venta) REFERENCES Venta (Id_Venta)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Fk_Detalle_Venta_Producto FOREIGN KEY (Id_Producto) REFERENCES Producto (Id_Producto)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT Ck_Detalle_Venta_Cantidad CHECK (Cantidad > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Notificaciones y personalización
-- ---------------------------------------------------------------------
CREATE TABLE Notificacion (
  Id_Notificacion INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Cliente      INT UNSIGNED NOT NULL,
  Tipo            ENUM('Confirmacion_Pedido','Cambio_Estado','Mensaje_Tienda','Producto_Disponible') NOT NULL,
  Asunto          VARCHAR(120) NOT NULL DEFAULT '',
  Destinatario    VARCHAR(20)  NOT NULL DEFAULT '' COMMENT 'Teléfono de WhatsApp',
  Contenido       TEXT         NOT NULL,
  Fecha_Envio     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Estado_Envio    ENUM('Enviado','Omitido') NOT NULL DEFAULT 'Enviado',
  Leida           TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (Id_Notificacion),
  KEY Ix_Notificacion_Cliente (Id_Cliente, Leida),
  CONSTRAINT Fk_Notificacion_Cliente FOREIGN KEY (Id_Cliente) REFERENCES Cliente (Id_Cliente)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Bandeja de mensajes del cliente y registro para WhatsApp';

CREATE TABLE Solicitud_Stock (
  Id_Solicitud INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Cliente   INT UNSIGNED NOT NULL,
  Id_Producto  INT UNSIGNED NOT NULL,
  Fecha        DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Atendida     TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (Id_Solicitud),
  KEY Ix_Solicitud_Cliente (Id_Cliente),
  KEY Ix_Solicitud_Producto (Id_Producto, Atendida),
  CONSTRAINT Fk_Solicitud_Cliente FOREIGN KEY (Id_Cliente) REFERENCES Cliente (Id_Cliente)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Fk_Solicitud_Producto FOREIGN KEY (Id_Producto) REFERENCES Producto (Id_Producto)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='"Avísame cuando llegue" de productos agotados';

CREATE TABLE Diseno_Personalizado (
  Id_Diseno         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_Cliente        INT UNSIGNED NOT NULL,
  Id_Producto_Base  INT UNSIGNED NULL,
  Descripcion       TEXT          NOT NULL,
  Imagen_Referencia VARCHAR(100)  NULL COMMENT 'Ruta en media/disenos/',
  Talla             VARCHAR(10)   NOT NULL,
  Color             VARCHAR(30)   NOT NULL,
  Cantidad          INT UNSIGNED  NOT NULL DEFAULT 1,
  Estado            ENUM('Solicitado','Cotizado','Aprobado','En_Produccion','Terminado','Rechazado') NOT NULL DEFAULT 'Solicitado',
  Precio_Cotizado   DECIMAL(10,2) NULL,
  Respuesta_Tienda  TEXT          NULL,
  Fecha             DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (Id_Diseno),
  KEY Ix_Diseno_Cliente (Id_Cliente),
  KEY Ix_Diseno_Producto (Id_Producto_Base),
  CONSTRAINT Fk_Diseno_Cliente FOREIGN KEY (Id_Cliente) REFERENCES Cliente (Id_Cliente)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Fk_Diseno_Producto FOREIGN KEY (Id_Producto_Base) REFERENCES Producto (Id_Producto)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Datos iniciales (los mismos del comando datos_demo, sin usuarios)
-- ---------------------------------------------------------------------
INSERT INTO Configuracion_Tienda (Nombre_Tienda) VALUES ('Dlune Pijamas');

INSERT INTO Categoria (Nombre) VALUES
  ('Navideña'), ('Invierno'), ('Verano'), ('Estampados animales');

INSERT INTO Producto (Codigo, Nombre, Descripcion, Id_Categoria, Genero, Colores, Stock, Precio_Compra, Porcentaje_Ganancia, Precio_Venta) VALUES
  ('PJ-001', 'Pijama Luna Estrellada', 'Pijama Luna Estrellada en algodón suave, ideal para dormir cómodo.', 1, 'Mujer',    'Azul,Negro',     20, 45000, 60, 72000),
  ('PJ-002', 'Pijama Ositos Polares',  'Pijama Ositos Polares en algodón suave, ideal para dormir cómodo.',  2, 'Infantil', 'Blanco,Rosa',     3, 30000, 60, 48000),
  ('PJ-003', 'Pijama Clásica Cuadros', 'Pijama Clásica Cuadros en algodón suave, ideal para dormir cómodo.', 2, 'Hombre',   'Rojo,Gris',      15, 50000, 60, 80000),
  ('PJ-004', 'Short Tropical',         'Short Tropical en algodón suave, ideal para dormir cómodo.',         3, 'Mujer',    'Verde,Amarillo',  0, 28000, 60, 44800),
  ('PJ-005', 'Pijama Dinosaurios',     'Pijama Dinosaurios en algodón suave, ideal para dormir cómodo.',     4, 'Infantil', 'Verde,Azul',     12, 32000, 60, 51200),
  ('PJ-006', 'Pijama Gatitos',         'Pijama Gatitos en algodón suave, ideal para dormir cómodo.',         4, 'Mujer',    'Rosa,Lila',       8, 42000, 60, 67200),
  ('PJ-007', 'Pijama Renos',           'Pijama Renos en algodón suave, ideal para dormir cómodo.',           1, 'Hombre',   'Rojo,Verde',      4, 48000, 60, 76800),
  ('PJ-008', 'Bermuda Palmeras',       'Bermuda Palmeras en algodón suave, ideal para dormir cómodo.',       3, 'Hombre',   'Azul,Blanco',    25, 26000, 60, 41600);

INSERT INTO Zona_Domicilio (Ciudad, Barrio, Costo) VALUES ('Medellín', '', 8000), ('Envigado', '', 10000);
INSERT INTO Cupon (Codigo, Porcentaje) VALUES ('DLUNE10', 10);
