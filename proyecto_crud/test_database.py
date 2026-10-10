import unittest
from unittest.mock import MagicMock

from database import Database
from validation import validar_email


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database.__new__(Database)
        self.conn = MagicMock()
        self.conn.is_connected.return_value = True
        self.db.conn = self.conn
        self.cursor = self.conn.cursor.return_value.__enter__.return_value

    def test_crear_usuario(self):
        self.cursor.lastrowid = 42

        resultado = self.db.crear_usuario("Juan", "juan@test.com")

        self.assertEqual(resultado, 42)
        self.cursor.execute.assert_called_once()
        self.conn.commit.assert_called_once()

    def test_crear_usuario_con_email_invalido(self):
        with self.assertRaises(ValueError):
            self.db.crear_usuario("Juan", "invalido")
        self.cursor.execute.assert_not_called()

    def test_obtener_usuarios(self):
        self.cursor.fetchall.return_value = [(42, "Juan", "juan@test.com")]

        resultado = self.db.obtener_usuarios()

        self.assertEqual(
            resultado,
            [{"id": 42, "nombre": "Juan", "email": "juan@test.com"}],
        )

    def test_obtener_por_email(self):
        self.cursor.fetchone.return_value = (42, "Juan", "juan@test.com")

        resultado = self.db.obtener_por_email("juan@test.com")

        self.assertEqual(
            resultado,
            {"id": 42, "nombre": "Juan", "email": "juan@test.com"},
        )

    def test_actualizar_y_eliminar(self):
        self.cursor.rowcount = 1

        self.assertTrue(self.db.actualizar("juan@test.com", "Juan Pérez"))
        self.assertTrue(self.db.eliminar("juan@test.com"))
        self.assertEqual(self.conn.commit.call_count, 2)

    def test_validar_email(self):
        self.assertTrue(validar_email("test@example.com"))
        self.assertFalse(validar_email("invalid"))


if __name__ == "__main__":
    unittest.main()
