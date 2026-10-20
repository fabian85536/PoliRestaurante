import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.administrador import Administrador
from models.administrador_DAO import AdministradorDAO
from models.mesa import Mesa
from models.mesa_DAO import MesaDAO
from models.mesero import Mesero
from models.mesero_DAO import MeseroDAO
from models.pedido import Pedido
from models.pedido_DAO import PedidoDAO
from models.personal_cocina import PersonalCocina
from models.usuario import Base


class TestEntidadesDAO(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.sesion = Session(self.engine, expire_on_commit=False)
        self.mesero_dao = MeseroDAO(self.sesion)
        self.administrador_dao = AdministradorDAO(self.sesion)
        self.mesa_dao = MesaDAO(self.sesion)
        self.pedido_dao = PedidoDAO(self.sesion)

    def tearDown(self):
        self.sesion.close()
        self.engine.dispose()

    def test_mesero_crud_sin_exponer_contrasena(self):
        mesero_id = self.mesero_dao.crear_mesero(" Ana ", "ana", "secreto")

        mesero = self.mesero_dao.obtener_por_id(mesero_id)
        self.assertEqual(mesero.nombre, "Ana")
        self.assertEqual(mesero.to_dict(), {
            "id_mesero": mesero_id,
            "nombre": "Ana",
            "usuario": "ana",
        })
        self.assertTrue(self.mesero_dao.actualizar(mesero_id, nombre="Ana María"))
        self.assertEqual(self.mesero_dao.obtener_por_id(mesero_id).nombre, "Ana María")
        self.assertEqual(len(self.mesero_dao.obtener_meseros()), 1)
        self.assertTrue(self.mesero_dao.eliminar(mesero_id))
        self.assertIsNone(self.mesero_dao.obtener_por_id(mesero_id))

    def test_administrador_crud_y_validacion(self):
        administrador_id = self.administrador_dao.crear_administrador(
            "Admin", "admin", "secreto"
        )

        self.assertEqual(len(self.administrador_dao.obtener_administradores()), 1)
        self.assertTrue(
            self.administrador_dao.actualizar(
                administrador_id, nombre="Administradora"
            )
        )
        self.assertEqual(
            self.administrador_dao.obtener_por_id(administrador_id).nombre,
            "Administradora",
        )
        with self.assertRaisesRegex(ValueError, "nombre es obligatorio"):
            self.administrador_dao.crear_administrador("", "admin2", "secreto")
        self.assertTrue(self.administrador_dao.eliminar(administrador_id))

    def test_mesa_crud_y_referencia_administrador(self):
        administrador = Administrador(
            nombre="Admin", usuario="admin", contrasena="secreto"
        )
        self.sesion.add(administrador)
        self.sesion.commit()
        mesa_id = self.mesa_dao.crear_mesa(
            1, "Disponible", administrador.id_administrador
        )

        mesa = self.mesa_dao.obtener_por_id(mesa_id)
        self.assertEqual(mesa.numero, 1)
        self.assertEqual(len(self.mesa_dao.obtener_mesas()), 1)
        self.assertTrue(self.mesa_dao.actualizar(mesa_id, estado="Ocupada"))
        self.assertEqual(self.mesa_dao.obtener_por_id(mesa_id).estado, "Ocupada")
        with self.assertRaisesRegex(ValueError, "No existe el administrador"):
            self.mesa_dao.crear_mesa(2, "Disponible", id_administrador=99)
        self.assertTrue(self.mesa_dao.eliminar(mesa_id))

    def test_pedido_crud_y_valida_todas_las_referencias(self):
        mesero = Mesero(nombre="Ana", usuario="ana", contrasena="secreto")
        administrador = Administrador(
            nombre="Admin", usuario="admin", contrasena="secreto"
        )
        cocina = PersonalCocina(nombre="Chef", usuario="chef", contrasena="secreto")
        self.sesion.add_all([mesero, administrador, cocina])
        self.sesion.commit()
        mesa_id = self.mesa_dao.crear_mesa(
            1, "Ocupada", administrador.id_administrador
        )
        pedido_id = self.pedido_dao.crear_pedido(
            id_mesero=mesero.id_mesero,
            id_cocina=cocina.id_cocina,
            id_administrador=administrador.id_administrador,
            id_mesa=mesa_id,
            tipo_pedido="Mesa",
            nombre_cliente="Carlos",
            estado="Pendiente",
            total=12000,
        )

        pedido = self.pedido_dao.obtener_por_id(pedido_id)
        self.assertEqual(pedido.total, 12000)
        self.assertEqual(len(self.pedido_dao.obtener_pedidos()), 1)
        self.assertTrue(
            self.pedido_dao.actualizar(
                pedido_id, estado="Entregado", metodo_pago="Efectivo"
            )
        )
        actualizado = self.pedido_dao.obtener_por_id(pedido_id)
        self.assertEqual(actualizado.estado, "Entregado")
        self.assertEqual(actualizado.metodo_pago, "Efectivo")
        with self.assertRaisesRegex(ValueError, "No existe el mesero con ID 99"):
            self.pedido_dao.crear_pedido(id_mesero=99)
        with self.assertRaisesRegex(ValueError, "no puede ser negativo"):
            self.pedido_dao.crear_pedido(total=-1)
        self.assertTrue(self.pedido_dao.eliminar(pedido_id))
        self.assertIsNone(self.pedido_dao.obtener_por_id(pedido_id))


if __name__ == "__main__":
    unittest.main()
