"""Catálogo inicial de Dlune: lo carga el comando `cargar_catalogo` con su foto en app_catalogo/imagenes_catalogo/.

Precio de venta = precio de compra x (1 + 60%). Las fotos son de Unsplash (licencia libre, ver
imagenes_catalogo/CREDITOS.md) y sirven de referencia mientras la tienda sube sus propias fotos.
"""

CATEGORIAS = {
    'Satín y elegancia': 'Pijamas de satín suave con acabados delicados.',
    'Algodón clásico': 'Pijamas frescas de algodón para todo el año.',
    'Franela invierno': 'Pijamas de franela gruesa para las noches frías.',
    'Verano': 'Shorts y prendas livianas para clima cálido.',
    'Infantil': 'Pijamas cómodas y resistentes para los más pequeños.',
    'Navideña': 'Colección especial de temporada para toda la familia.',
    'Parejas y familia': 'Juegos de pijamas iguales para compartir.',
}

CUIDADO = 'Lavar a máquina en agua fría, no usar blanqueador y secar a la sombra.'

PRODUCTOS = [
    # codigo, nombre, categoria, genero, precio_compra, tallas, colores, stock, descripción, foto de Unsplash
    ('DL-001', 'Pijama Satín Azul Noche', 'Satín y elegancia', 'mujer', 55000, 'S,M,L,XL', 'Azul noche', 18,
     'Camisa de manga larga con bolsillo y pantalón largo en satín suave. Ribete blanco en cuello, puños y bolsillo.',
     'photo-1766056278944-ca0e4f49e61f'),
    ('DL-002', 'Pijama Rosa Clásica', 'Algodón clásico', 'mujer', 40000, 'S,M,L', 'Rosa', 22,
     'Conjunto de camisa abotonada y pantalón largo en algodón texturizado. Ribete blanco y botones en contraste.',
     'photo-1768696082668-411638a55476'),
    ('DL-003', 'Pijama Satín Rosa Perla', 'Satín y elegancia', 'mujer', 55000, 'S,M,L,XL', 'Rosa perla', 12,
     'Satín jacquard con brillo sutil. Camisa con cuello solapa y pantalón de bota recta.',
     'photo-1766056278885-5ab8a9ff351a'),
    ('DL-004', 'Pijama Flores Blanco y Negro', 'Algodón clásico', 'mujer', 45000, 'XS,S,M,L', 'Negro,Blanco', 9,
     'Algodón suave con estampado floral en blanco y negro. Camisa de manga tres cuartos y pantalón amplio.',
     'photo-1762777777692-256d7050df9a'),
    ('DL-005', 'Pijama Franela Cuadros Rojos', 'Franela invierno', 'hombre', 60000, 'M,L,XL,XXL', 'Rojo,Verde', 15,
     'Franela 100% algodón perchada por dentro. Diseño clásico de cuadros escoceses, camisa con bolsillo.',
     'photo-1604936509922-a0ae4fd19e3e'),
    ('DL-006', 'Pijama Rayas Clásicas', 'Satín y elegancia', 'mujer', 55000, 'S,M,L,XL', 'Beige,Negro', 20,
     'Satín con rayas verticales en beige y negro. Camisa con cuello solapa, bolsillo y pantalón largo.',
     'photo-1766056278967-c0646b1bfd67'),
    ('DL-007', 'Pijama Satín Rojo Short', 'Verano', 'hombre', 45000, 'M,L,XL', 'Rojo', 25,
     'Camisa de manga corta y short en satín rojo con ribete blanco. Fresca para noches calurosas.',
     'photo-1612975828131-845f5bdb8676'),
    ('DL-008', 'Pijama Crema Ribete Negro', 'Algodón clásico', 'hombre', 45000, 'M,L,XL', 'Crema', 4,
     'Conjunto de camisa abotonada y pantalón largo color crema con ribete negro. Tela suave y transpirable.',
     'photo-1768696083097-600943ad9d05'),
    ('DL-009', 'Pijama Bebé Azul Petróleo', 'Infantil', 'infantil', 25000, '6M,12M,18M,2', 'Azul petróleo', 16,
     'Pijama de manga corta para bebé en algodón hipoalergénico. Costuras suaves que no irritan la piel.',
     'photo-1602863211758-e35574d21b22'),
    ('DL-010', 'Pijama Infantil Rosa Estampada', 'Infantil', 'infantil', 30000, '2,4,6,8', 'Rosa', 14,
     'Conjunto infantil de manga larga con estampado. Algodón suave que no destiñe y resorte cómodo en la cintura.',
     'photo-1771419912747-df33d91c329d'),
    ('DL-011', 'Pijama Infantil Rosa Algodón', 'Infantil', 'infantil', 30000, '2,4,6,8,10', 'Rosa,Blanco', 3,
     'Pijama infantil de algodón con puños ajustables. Ideal para jugar y dormir.',
     'photo-1678979617936-1ed6fa406b67'),
    ('DL-012', 'Pijama Estrellas Gris', 'Infantil', 'infantil', 30000, '4,6,8,10,12', 'Gris', 10,
     'Pijama de algodón gris con estrellas blancas. Camiseta de manga larga y pantalón con puños.',
     'photo-1573258517406-4a3824f3a476'),
    ('DL-013', 'Pijama Navidad Cuadros Búfalo', 'Navideña', 'hombre', 55000, 'S,M,L,XL', 'Rojo,Negro', 8,
     'Edición navideña con cuadros búfalo rojo y negro. Combina con la versión de mujer y niños.',
     'photo-1670906230394-d5b332a2113b'),
    ('DL-014', 'Pijama Satín Rojo y Dorado', 'Navideña', 'mujer', 60000, 'S,M,L,XL', 'Rojo,Dorado', 0,
     'Satín rojo con estampado dorado, perfecta para las fiestas. Agotada por temporada: pide que te avisemos cuando llegue.',
     'photo-1654512462970-8191bc8742bd'),
    ('DL-015', 'Pijama Navidad Niños', 'Navideña', 'infantil', 30000, '2,4,6,8,10', 'Rojo,Blanco', 11,
     'Versión infantil de la colección navideña familiar. Perfecta para las fotos de diciembre.',
     'photo-1606916693216-69bd7e1cf2fa'),
    ('DL-016', 'Kit Pareja Cuadros Rojos', 'Parejas y familia', 'mujer', 75000, 'S,M,L,XL', 'Rojo,Negro', 6,
     'Juego de dos pijamas iguales de cuadros rojos (tallas por separado). El regalo ideal para compartir.',
     'photo-1762444015432-bf564dc27613'),
]
