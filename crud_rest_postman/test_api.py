import tempfile
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import create_app
from models.usuario import Base


class SQLiteDatabase:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.engine = None
        self.sesion = None

    def conectar(self):
        self.engine = create_engine(f"sqlite:///{self.database_path}")
        self.sesion = Session(self.engine, expire_on_commit=False)

    def desconectar(self):
        if self.sesion is not None:
            self.sesion.close()
            self.sesion = None
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None


class RestApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test.db"
        engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(engine)
        engine.dispose()
        self.app = create_app(
            database_factory=lambda: SQLiteDatabase(database_path)
        )
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def response_json(self, response):
        payload = response.get_json()
        if not isinstance(payload, dict):
            raise AssertionError("La respuesta no contiene un objeto JSON.")
        return payload

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_does_not_require_a_database(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_user_crud_and_passwords_are_not_returned(self):
        created = self.client.post(
            "/api/usuarios",
            json={"nombre": "Ana", "email": "ana@example.com"},
        )
        self.assertEqual(created.status_code, 201)
        created_json = self.response_json(created)
        user_id = created_json["id"]
        self.assertEqual(created_json["nombre"], "Ana")

        updated = self.client.patch(
            f"/api/usuarios/{user_id}", json={"nombre": "Ana Ruiz"}
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.response_json(updated)["nombre"], "Ana Ruiz")
        self.assertEqual(self.client.get("/api/usuarios").status_code, 200)
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/usuarios/{user_id}")
            )["email"],
            "ana@example.com",
        )
        self.assertEqual(
            self.client.delete(f"/api/usuarios/{user_id}").status_code, 204
        )
        self.assertEqual(
            self.client.get(f"/api/usuarios/{user_id}").status_code, 404
        )

        staff = self.client.post(
            "/api/meseros",
            json={
                "nombre": "Luis",
                "usuario": "luis",
                "contrasena": "secreto",
            },
        )
        self.assertEqual(staff.status_code, 201)
        staff_json = self.response_json(staff)
        staff_id = staff_json["id_mesero"]
        self.assertNotIn("contrasena", staff_json)
        self.assertEqual(
            self.client.get("/api/meseros").status_code, 200
        )
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/meseros/{staff_id}")
            )["usuario"],
            "luis",
        )
        self.assertEqual(
            self.client.patch(
                f"/api/meseros/{staff_id}", json={"nombre": "Luis Pérez"}
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/api/meseros/{staff_id}").status_code, 204
        )

    def test_product_and_order_crud(self):
        product = self.client.post(
            "/api/productos",
            json={"nombre": "Jugo", "precio": 8000, "disponible": True},
        )
        self.assertEqual(product.status_code, 201)
        product_json = self.response_json(product)
        product_id = product_json["id"]
        self.assertTrue(product_json["disponible"])
        self.assertEqual(
            self.client.get("/api/productos").status_code, 200
        )
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/productos/{product_id}")
            )["nombre"],
            "Jugo",
        )

        updated_product = self.client.patch(
            f"/api/productos/{product_id}",
            json={"disponible": False},
        )
        self.assertEqual(updated_product.status_code, 200)
        self.assertFalse(
            self.response_json(updated_product)["disponible"]
        )
        self.assertEqual(
            self.client.delete(f"/api/productos/{product_id}").status_code,
            204,
        )

        order = self.client.post(
            "/api/pedidos",
            json={"tipo_pedido": "Mesa", "total": 8000},
        )
        self.assertEqual(order.status_code, 201)
        order_id = self.response_json(order)["id_pedido"]
        self.assertEqual(
            self.client.get("/api/pedidos").status_code, 200
        )
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/pedidos/{order_id}")
            )["tipo_pedido"],
            "Mesa",
        )
        updated_order = self.client.patch(
            f"/api/pedidos/{order_id}", json={"estado": "Abierto"}
        )
        self.assertEqual(
            self.response_json(updated_order)["estado"], "Abierto"
        )
        self.assertEqual(
            self.client.delete(f"/api/pedidos/{order_id}").status_code, 204
        )

    def test_table_and_admin_crud(self):
        admin = self.client.post(
            "/api/administradores",
            json={
                "nombre": "Marta",
                "usuario": "marta",
                "contrasena": "secreto",
            },
        )
        self.assertEqual(admin.status_code, 201)
        admin_json = self.response_json(admin)
        admin_id = admin_json["id_administrador"]
        self.assertNotIn("contrasena", admin_json)
        self.assertEqual(
            self.client.get("/api/administradores").status_code, 200
        )
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/administradores/{admin_id}")
            )["usuario"],
            "marta",
        )
        self.assertEqual(
            self.client.patch(
                f"/api/administradores/{admin_id}",
                json={"nombre": "Marta Pérez"},
            ).status_code,
            200,
        )
        table = self.client.post(
            "/api/mesas",
            json={
                "numero": 1,
                "estado": "Libre",
                "id_administrador": admin_id,
            },
        )
        self.assertEqual(table.status_code, 201)
        table_id = self.response_json(table)["id_mesa"]
        self.assertEqual(self.client.get("/api/mesas").status_code, 200)
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/mesas/{table_id}")
            )["estado"],
            "Libre",
        )
        self.assertEqual(
            self.response_json(
                self.client.patch(
                    f"/api/mesas/{table_id}", json={"estado": "Ocupada"}
                )
            )["estado"],
            "Ocupada",
        )
        self.assertEqual(
            self.client.delete(f"/api/mesas/{table_id}").status_code, 204
        )
        self.assertEqual(
            self.client.delete(f"/api/administradores/{admin_id}").status_code,
            204,
        )

    def test_invalid_payload_and_unknown_resource(self):
        invalid = self.client.post(
            "/api/usuarios", json={"nombre": "Ana"}
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("error", self.response_json(invalid))
        self.assertEqual(self.client.get("/api/desconocido").status_code, 404)


if __name__ == "__main__":
    unittest.main()
