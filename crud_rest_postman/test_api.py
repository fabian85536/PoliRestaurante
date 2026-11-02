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
        self.engine_creations = 0
        self.sessions_created = 0

    def nueva_sesion(self):
        if self.engine is None:
            self.engine = create_engine(f"sqlite:///{self.database_path}")
            self.engine_creations += 1
        self.sessions_created += 1
        return Session(self.engine, expire_on_commit=False)

    def desconectar(self):
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
        self.database = SQLiteDatabase(database_path)
        self.app = create_app(database_factory=lambda: self.database)
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def response_json(self, response):
        payload = response.get_json()
        if not isinstance(payload, dict):
            raise AssertionError("La respuesta no contiene un objeto JSON.")
        return payload

    def tearDown(self):
        self.database.desconectar()
        self.temp_dir.cleanup()

    def test_health_does_not_require_a_database(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_requests_reuse_engine_and_create_a_session_per_request(self):
        self.client.get("/api/usuarios")
        self.client.post(
            "/api/usuarios",
            json={"nombre": "Ana", "email": "ana@example.com"},
        )
        self.client.get("/api/usuarios")

        self.assertEqual(self.database.engine_creations, 1)
        self.assertEqual(self.database.sessions_created, 3)

    def test_cors_allows_live_server_origins_and_json_preflight(self):
        for origin in (
            "http://127.0.0.1:5500",
            "http://localhost:5500",
        ):
            response = self.client.get("/health", headers={"Origin": origin})
            self.assertEqual(
                response.headers.get("Access-Control-Allow-Origin"), origin
            )

        preflight = self.client.options(
            "/api/usuarios",
            headers={
                "Origin": "http://127.0.0.1:5500",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        self.assertEqual(preflight.status_code, 200)
        self.assertEqual(
            preflight.headers.get("Access-Control-Allow-Origin"),
            "http://127.0.0.1:5500",
        )
        self.assertIn(
            "content-type",
            preflight.headers.get("Access-Control-Allow-Headers", "").lower(),
        )

    def test_cors_does_not_allow_unconfigured_origins(self):
        response = self.client.get(
            "/health", headers={"Origin": "http://example.com"}
        )
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)

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
        updated_staff = self.client.patch(
            f"/api/meseros/{staff_id}",
            json={
                "nombre": "María García Actualizada",
                "usuario": "mgarcia2",
                "contrasena": "clave789",
            },
        )
        updated_staff_json = self.response_json(updated_staff)
        self.assertEqual(updated_staff.status_code, 200)
        self.assertEqual(updated_staff_json["id_mesero"], staff_id)
        self.assertEqual(updated_staff_json["nombre"], "María García Actualizada")
        self.assertEqual(updated_staff_json["usuario"], "mgarcia2")
        self.assertNotIn("contrasena", updated_staff_json)
        self.assertEqual(
            self.client.patch(
                f"/api/meseros/{staff_id}", json={"nombre": "Luis Pérez"}
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/api/meseros/{staff_id}").status_code, 204
        )

    def test_personal_cocina_crud_and_password_is_not_returned(self):
        created = self.client.post(
            "/api/personal_cocina",
            json={
                "nombre": "Chef",
                "usuario": "chef",
                "contrasena": "secreto",
            },
        )
        self.assertEqual(created.status_code, 201)
        created_json = self.response_json(created)
        cocina_id = created_json["id_cocina"]
        self.assertNotIn("contrasena", created_json)
        records = self.client.get("/api/personal_cocina").get_json()
        self.assertIsInstance(records, list)
        self.assertEqual(records[0]["usuario"], "chef")
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/personal_cocina/{cocina_id}")
            )["nombre"],
            "Chef",
        )
        updated = self.client.patch(
            f"/api/personal_cocina/{cocina_id}",
            json={"nombre": "Chef principal"},
        )
        self.assertEqual(
            self.response_json(updated)["nombre"], "Chef principal"
        )
        self.assertEqual(
            self.client.delete(f"/api/personal_cocina/{cocina_id}").status_code,
            204,
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

    def test_home_delivery_and_order_detail_crud(self):
        order = self.client.post(
            "/api/pedidos", json={"tipo_pedido": "Domicilio"}
        )
        self.assertEqual(order.status_code, 201)
        order_id = self.response_json(order)["id_pedido"]
        product = self.client.post(
            "/api/productos",
            json={"nombre": "Jugo", "precio": 5000},
        )
        self.assertEqual(product.status_code, 201)
        product_id = self.response_json(product)["id"]

        delivery = self.client.post(
            "/api/domicilios",
            json={
                "id_pedido": order_id,
                "direccion": "Calle 1",
                "telefono": "3001234567",
                "costo_envio": 5000,
            },
        )
        self.assertEqual(delivery.status_code, 201)
        delivery_id = self.response_json(delivery)["id_domicilio"]
        self.assertEqual(self.client.get("/api/domicilios").status_code, 200)
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/domicilios/{delivery_id}")
            )["direccion"],
            "Calle 1",
        )
        self.assertEqual(
            self.client.post(
                "/api/domicilios",
                json={"id_pedido": order_id},
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.patch(
                f"/api/domicilios/{delivery_id}",
                json={"direccion": "Carrera 2"},
            ).status_code,
            200,
        )

        detail = self.client.post(
            "/api/detalles_pedido",
            json={
                "id_pedido": order_id,
                "id_producto": product_id,
                "cantidad": 2,
                "precio_unitario": 5000,
                "notas": "Sin hielo",
            },
        )
        self.assertEqual(detail.status_code, 201)
        detail_id = self.response_json(detail)["id_detalle"]
        self.assertEqual(
            self.client.get("/api/detalles_pedido").status_code, 200
        )
        self.assertEqual(
            self.response_json(
                self.client.get(f"/api/detalles_pedido/{detail_id}")
            )["notas"],
            "Sin hielo",
        )
        self.assertEqual(
            self.client.patch(
                f"/api/detalles_pedido/{detail_id}",
                json={"cantidad": 3},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                "/api/detalles_pedido",
                json={"id_pedido": order_id, "id_producto": 999},
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.delete(f"/api/detalles_pedido/{detail_id}").status_code,
            204,
        )
        self.assertEqual(
            self.client.delete(f"/api/domicilios/{delivery_id}").status_code,
            204,
        )

    def test_create_order_with_details_uses_both_daos_atomically(self):
        product = self.client.post(
            "/api/productos",
            json={"nombre": "Jugo", "precio": 5000},
        )
        self.assertEqual(product.status_code, 201)
        product_id = self.response_json(product)["id"]

        created = self.client.post(
            "/api/pedidos/con-detalles",
            json={
                "pedido": {
                    "tipo_pedido": "Mesa",
                    "nombre_cliente": "Ana",
                    "total": 10000,
                },
                "detalles": [
                    {
                        "id_producto": product_id,
                        "cantidad": 2,
                        "precio_unitario": 5000,
                    },
                    {
                        "id_producto": product_id,
                        "cantidad": 1,
                        "precio_unitario": 5000,
                        "notas": "Sin hielo",
                    },
                ],
            },
        )
        self.assertEqual(created.status_code, 201)
        response = self.response_json(created)
        self.assertEqual(response["pedido"]["nombre_cliente"], "Ana")
        self.assertEqual(len(response["detalles"]), 2)
        order_id = response["pedido"]["id_pedido"]
        self.assertEqual(
            self.client.get(f"/api/pedidos/{order_id}").status_code, 200
        )
        self.assertEqual(
            len(
                [
                    detalle
                    for detalle in self.client.get(
                        "/api/detalles_pedido"
                    ).json
                    if detalle["id_pedido"] == order_id
                ]
            ),
            2,
        )

        rejected = self.client.post(
            "/api/pedidos/con-detalles",
            json={
                "pedido": {"tipo_pedido": "Domicilio"},
                "detalles": [
                    {
                        "id_producto": product_id,
                        "cantidad": 0,
                        "precio_unitario": 5000,
                    }
                ],
            },
        )
        self.assertEqual(rejected.status_code, 400)
        self.assertEqual(
            len(
                [
                    pedido
                    for pedido in self.client.get("/api/pedidos").json
                    if pedido["tipo_pedido"] == "Domicilio"
                ]
            ),
            0,
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
