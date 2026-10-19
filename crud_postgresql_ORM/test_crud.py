import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from crud import UsuarioCRUD
from database import crear_engine as crear_engine_postgresql
from models import Base, Usuario


class TestUsuarioCRUD(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine, expire_on_commit=False)
        self.crud = UsuarioCRUD(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_crear_listar_buscar_actualizar_y_eliminar(self):
        usuario = self.crud.crear(" Ana ", "ana@example.com")

        self.assertEqual((usuario.nombre, usuario.email), ("Ana", "ana@example.com"))
        self.assertEqual(self.crud.listar(), [usuario])
        self.assertIs(self.crud.obtener(usuario.id), usuario)

        self.assertTrue(
            self.crud.actualizar(usuario.id, "Ana María", "ana.maria@example.com")
        )
        self.assertEqual(self.crud.obtener(usuario.id).nombre, "Ana María")
        self.assertTrue(self.crud.eliminar(usuario.id))
        self.assertIsNone(self.crud.obtener(usuario.id))

    def test_rechaza_datos_invalidos(self):
        with self.assertRaisesRegex(ValueError, "El nombre es obligatorio"):
            self.crud.crear("  ", "ana@example.com")
        with self.assertRaisesRegex(ValueError, "El email no es válido"):
            self.crud.crear("Ana", "invalido")

    def test_email_duplicado_revierte_transaccion(self):
        self.crud.crear("Ana", "ana@example.com")
        with self.assertRaisesRegex(ValueError, "Ya existe un usuario"):
            self.crud.crear("Otra Ana", "ana@example.com")

        self.crud.crear("Luis", "luis@example.com")
        self.assertEqual(len(self.crud.listar()), 2)

    def test_actualizar_email_duplicado_no_cambia_el_usuario(self):
        ana = self.crud.crear("Ana", "ana@example.com")
        self.crud.crear("Luis", "luis@example.com")

        with self.assertRaisesRegex(ValueError, "Ya existe un usuario"):
            self.crud.actualizar(ana.id, email="luis@example.com")

        self.assertEqual(self.crud.obtener(ana.id).email, "ana@example.com")

    def test_operaciones_indican_si_el_usuario_no_existe(self):
        self.assertIsNone(self.crud.obtener(999))
        self.assertFalse(self.crud.actualizar(999, nombre="Ana"))
        self.assertFalse(self.crud.eliminar(999))

    def test_url_indicada_crea_engine_postgresql_sin_conectar(self):
        engine = crear_engine_postgresql("postgresql://user:pass@localhost/db")
        try:
            self.assertEqual(engine.dialect.name, "postgresql")
        finally:
            engine.dispose()

    def test_url_de_conexion_es_obligatoria(self):
        with self.assertRaisesRegex(ValueError, "Configura DATABASE_URL"):
            crear_engine_postgresql("")

    def test_rechaza_otro_dialecto(self):
        with self.assertRaisesRegex(ValueError, "debe usar el dialecto PostgreSQL"):
            crear_engine_postgresql("sqlite:///:memory:")


if __name__ == "__main__":
    unittest.main()
