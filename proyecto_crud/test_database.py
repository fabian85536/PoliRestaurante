import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.usuario import Usuario
from models.usuario_DAO import UsuarioDAO
from validation import validar_email


class TestUsuarioDAO(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Usuario.metadata.create_all(self.engine)
        self.sesion = Session(self.engine, expire_on_commit=False)
        self.dao = UsuarioDAO(self.sesion)

    def tearDown(self):
        self.sesion.close()
        self.engine.dispose()

    def test_crear_usuario(self):
        resultado = self.dao.crear_usuario("Juan", "juan@test.com")

        usuario = self.sesion.scalar(select(Usuario))
        self.assertEqual(resultado, usuario.id)
        self.assertEqual(usuario.nombre, "Juan")
        self.assertEqual(usuario.email, "juan@test.com")

    def test_crear_usuario_con_email_invalido(self):
        with self.assertRaises(ValueError):
            self.dao.crear_usuario("Juan", "invalido")
        self.assertEqual(self.dao.obtener_usuarios(), [])

    def test_email_duplicado_revierte_la_transaccion(self):
        self.dao.crear_usuario("Juan", "juan@test.com")

        with self.assertRaises(IntegrityError):
            self.dao.crear_usuario("Otro Juan", "juan@test.com")

        self.dao.crear_usuario("Ana", "ana@test.com")
        self.assertEqual(len(self.dao.obtener_usuarios()), 2)

    def test_obtener_usuarios(self):
        self.dao.crear_usuario("Juan", "juan@test.com")

        resultado = self.dao.obtener_usuarios()

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].nombre, "Juan")
        self.assertEqual(resultado[0].email, "juan@test.com")

    def test_obtener_por_email(self):
        self.dao.crear_usuario("Juan", "juan@test.com")

        resultado = self.dao.obtener_por_email("juan@test.com")

        self.assertIsInstance(resultado, Usuario)
        self.assertEqual(resultado.nombre, "Juan")

    def test_obtener_usuario_inexistente(self):
        self.assertIsNone(self.dao.obtener_por_email("no-existe@test.com"))

    def test_actualizar_y_eliminar(self):
        self.dao.crear_usuario("Juan", "juan@test.com")

        self.assertTrue(self.dao.actualizar("juan@test.com", "Juan Pérez"))
        self.assertEqual(self.dao.obtener_por_email("juan@test.com").nombre, "Juan Pérez")
        self.assertTrue(self.dao.eliminar("juan@test.com"))
        self.assertIsNone(self.dao.obtener_por_email("juan@test.com"))

    def test_validar_email(self):
        self.assertTrue(validar_email("test@example.com"))
        self.assertFalse(validar_email("invalid"))


if __name__ == "__main__":
    unittest.main()
