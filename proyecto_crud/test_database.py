import unittest
from unittest.mock import MagicMock

from models.usuario import Usuario
from models.usuario_DAO import UsuarioDAO
from validation import validar_email


class TestUsuarioDAO(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.conn.is_connected.return_value = True
        self.dao = UsuarioDAO(self.conn)
        self.cursor = self.conn.cursor.return_value.__enter__.return_value

    def test_crear_usuario(self):
        self.cursor.lastrowid = 42

        resultado = self.dao.crear_usuario("Juan", "juan@test.com")

        self.assertEqual(resultado, 42)
        self.cursor.execute.assert_called_once()
        self.conn.commit.assert_called_once()

    def test_crear_usuario_con_email_invalido(self):
        with self.assertRaises(ValueError):
            self.dao.crear_usuario("Juan", "invalido")
        self.cursor.execute.assert_not_called()

    def test_obtener_usuarios(self):
        self.cursor.fetchall.return_value = [(42, "Juan", "juan@test.com")]

        resultado = self.dao.obtener_usuarios()

        self.assertEqual(
            resultado,
            [Usuario(42, "Juan", "juan@test.com")],
        )

    def test_obtener_por_email(self):
        self.cursor.fetchone.return_value = (42, "Juan", "juan@test.com")

        resultado = self.dao.obtener_por_email("juan@test.com")

        self.assertEqual(resultado, Usuario(42, "Juan", "juan@test.com"))

    def test_actualizar_y_eliminar(self):
        self.cursor.rowcount = 1

        self.assertTrue(self.dao.actualizar("juan@test.com", "Juan Pérez"))
        self.assertTrue(self.dao.eliminar("juan@test.com"))
        self.assertEqual(self.conn.commit.call_count, 2)

    def test_operacion_sin_conexion(self):
        self.conn.is_connected.return_value = False

        with self.assertRaises(RuntimeError):
            self.dao.obtener_usuarios()

    def test_validar_email(self):
        self.assertTrue(validar_email("test@example.com"))
        self.assertFalse(validar_email("invalid"))


if __name__ == "__main__":
    unittest.main()
