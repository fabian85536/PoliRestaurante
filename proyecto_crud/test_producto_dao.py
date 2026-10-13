import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.Producto import Administrador, Categoria, Producto
from models.producto_DAO import ProductoDAO


class TestProductoDAO(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Producto.metadata.create_all(self.engine)
        self.sesion = Session(self.engine, expire_on_commit=False)
        self.dao = ProductoDAO(self.sesion)

    def tearDown(self):
        self.sesion.close()
        self.engine.dispose()

    def test_crear_listar_buscar_actualizar_y_eliminar_producto(self):
        categoria = Categoria(nombre="Platos")
        administrador = Administrador(nombre="Admin")
        self.sesion.add_all([categoria, administrador])
        self.sesion.commit()
        producto_id = self.dao.crear_producto(
            "Hamburguesa",
            "Con queso",
            12000,
            id_categoria=categoria.id_categoria,
            id_administrador=administrador.id_administrador,
            disponible=True,
        )

        producto = self.dao.obtener_por_id(producto_id)
        self.assertIsNotNone(producto)
        assert producto is not None
        self.assertEqual(producto.nombre, "Hamburguesa")
        self.assertEqual(producto.precio, 12000)
        self.assertTrue(producto.disponible)
        self.assertEqual(len(self.dao.obtener_productos()), 1)

        self.assertTrue(
            self.dao.actualizar(
                producto_id, nombre="Hamburguesa doble", disponible=False
            )
        )
        actualizado = self.dao.obtener_por_id(producto_id)
        self.assertIsNotNone(actualizado)
        assert actualizado is not None
        self.assertEqual(actualizado.nombre, "Hamburguesa doble")
        self.assertFalse(actualizado.disponible)

        self.assertTrue(self.dao.eliminar(producto_id))
        self.assertIsNone(self.dao.obtener_por_id(producto_id))

    def test_rechaza_categoria_o_administrador_inexistente(self):
        with self.assertRaisesRegex(ValueError, "No existe la categoría con ID 1"):
            self.dao.crear_producto(
                "Sopa",
                "Caliente",
                100,
                id_categoria=1,
            )
        with self.assertRaisesRegex(
            ValueError, "No existe el administrador con ID 12"
        ):
            self.dao.crear_producto(
                "Sopa",
                "Caliente",
                100,
                id_administrador=12,
            )

        self.assertEqual(self.dao.obtener_productos(), [])

    def test_actualizacion_rechaza_categoria_inexistente_sin_modificar_producto(self):
        producto_id = self.dao.crear_producto("Sopa", "Caliente", 100)

        with self.assertRaisesRegex(ValueError, "No existe la categoría con ID 1"):
            self.dao.actualizar(producto_id, id_categoria=1)

        producto = self.dao.obtener_por_id(producto_id)
        self.assertIsNotNone(producto)
        assert producto is not None
        self.assertIsNone(producto.id_categoria)

    def test_rechaza_producto_sin_nombre_o_precio_valido(self):
        with self.assertRaises(ValueError):
            self.dao.crear_producto("", "Descripción", 1000)
        with self.assertRaises(ValueError):
            self.dao.crear_producto("Producto", "Descripción", 0)

        self.assertEqual(self.dao.obtener_productos(), [])


if __name__ == "__main__":
    unittest.main()
