import unittest

from ejemplo_usuarios import app, usuarios


class EjemploUsuariosTests(unittest.TestCase):
    def setUp(self):
        usuarios.clear()
        usuarios.extend(
            [
                {"id": 1, "nombre": "Juan", "email": "juan@ex.com"},
                {"id": 2, "nombre": "Maria", "email": "maria@ex.com"},
            ]
        )
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_get_list_and_user_by_both_routes(self):
        response = self.client.get("/api/usuarios")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [
                {"id": 1, "nombre": "Juan", "email": "juan@ex.com"},
                {"id": 2, "nombre": "Maria", "email": "maria@ex.com"},
            ],
        )

        for path in ("/api/usuarios/1", "/usuario/1"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["nombre"], "Juan")

        self.assertEqual(self.client.get("/usuario/999").status_code, 404)

    def test_post_create_validate_and_generate_id(self):
        response = self.client.post(
            "/crear",
            json={"nombre": "Ana", "email": "ana@example.com", "edad": 25},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 3)
        self.assertEqual(response.get_json()["edad"], 25)
        self.assertEqual(response.headers["Location"], "/api/usuarios/3")

        invalid = self.client.post("/api/usuarios", json={"email": "x@example.com"})
        self.assertEqual(invalid.status_code, 400)

        invalid_age = self.client.post(
            "/api/usuarios", json={"nombre": "Luis", "edad": True}
        )
        self.assertEqual(invalid_age.status_code, 400)

    def test_put_update_and_not_found(self):
        response = self.client.put(
            "/api/usuarios/1",
            json={"nombre": "Juan Pérez", "email": "jp@example.com", "edad": 30},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["nombre"], "Juan Pérez")
        self.assertEqual(response.get_json()["edad"], 30)
        self.assertEqual(
            self.client.put("/api/usuarios/999", json={"nombre": "Nadie"}).status_code,
            404,
        )

    def test_delete_existing_and_missing_users(self):
        response = self.client.delete("/api/usuarios/1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(), b"")
        self.assertEqual(self.client.get("/api/usuarios/1").status_code, 404)
        self.assertEqual(self.client.delete("/api/usuarios/999").status_code, 404)

    def test_calculator_and_json_error_handlers(self):
        response = self.client.get("/calcular?numero=42")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"resultado": 42})

        default = self.client.get("/calcular")
        self.assertEqual(default.status_code, 200)
        self.assertEqual(default.get_json(), {"resultado": 0})

        invalid = self.client.get("/calcular?numero=abc")
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(invalid.get_json(), {"error": "Número inválido"})

        not_found = self.client.get("/ruta-inexistente")
        self.assertEqual(not_found.status_code, 404)
        self.assertEqual(
            not_found.get_json(), {"error": "Recurso no encontrado"}
        )


if __name__ == "__main__":
    unittest.main()
