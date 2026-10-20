import logging

from flask import Flask, jsonify, request

app = Flask(__name__)

usuarios = [
    {"id": 1, "nombre": "Juan", "email": "juan@ex.com", "edad": 0},
    {"id": 2, "nombre": "Maria", "email": "maria@ex.com", "edad": 0},
]


@app.errorhandler(404)
def no_encontrado(_error):
    return jsonify(error="Recurso no encontrado"), 404


@app.errorhandler(500)
def error_servidor(error):
    logging.error("Error interno en el ejemplo REST: %s", error)
    return jsonify(error="Error interno del servidor"), 500


def obtener_datos():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return None, (jsonify(error="El cuerpo debe ser un objeto JSON."), 400)
    return datos, None


@app.get("/")
def inicio():
    return jsonify(
        mensaje="API de ejemplo para Postman",
        rutas=[
            "GET /api/usuarios",
            "GET /api/usuarios/<id>",
            "POST /api/usuarios",
            "PUT /api/usuarios/<id>",
            "DELETE /api/usuarios/<id>",
            "GET /calcular?numero=<entero>",
        ],
    )


@app.get("/calcular")
def calcular():
    try:
        resultado = int(request.args.get("numero", 0))
    except ValueError:
        return jsonify(error="Número inválido"), 400
    return jsonify(resultado=resultado), 200


@app.get("/api/usuarios")
def obtener_usuarios():
    return jsonify(usuarios), 200


@app.get("/api/usuarios/<int:usuario_id>")
@app.get("/usuario/<int:usuario_id>")
def obtener_usuario(usuario_id):
    usuario = next((item for item in usuarios if item["id"] == usuario_id), None)
    if usuario is None:
        return jsonify(error="No encontrado"), 404
    return jsonify(usuario), 200


@app.post("/api/usuarios")
@app.post("/crear")
def crear_usuario():
    datos, error = obtener_datos()
    if error:
        return error

    nombre = datos.get("nombre")
    email = datos.get("email", "")
    edad = datos.get("edad", 0)
    if not isinstance(nombre, str) or not nombre.strip():
        return jsonify(error="El nombre es obligatorio."), 400
    if not isinstance(email, str):
        return jsonify(error="El email debe ser texto."), 400
    if isinstance(edad, bool) or not isinstance(edad, int) or edad < 0:
        return jsonify(error="La edad debe ser un entero no negativo."), 400

    nuevo_id = max((usuario["id"] for usuario in usuarios), default=0) + 1
    nuevo_usuario = {
        "id": nuevo_id,
        "nombre": nombre.strip(),
        "email": email.strip(),
        "edad": edad,
    }
    usuarios.append(nuevo_usuario)
    response = jsonify(nuevo_usuario)
    response.status_code = 201
    response.headers["Location"] = f"/api/usuarios/{nuevo_id}"
    return response


@app.put("/api/usuarios/<int:usuario_id>")
def actualizar_usuario(usuario_id):
    usuario = next((item for item in usuarios if item["id"] == usuario_id), None)
    if usuario is None:
        return jsonify(error="No encontrado"), 404

    datos, error = obtener_datos()
    if error:
        return error

    campos_permitidos = {"nombre", "email", "edad"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        return jsonify(
            error="Campos no válidos: " + ", ".join(sorted(campos_desconocidos))
        ), 400

    nombre = datos.get("nombre", usuario["nombre"])
    email = datos.get("email", usuario["email"])
    edad = datos.get("edad", usuario["edad"])
    if not isinstance(nombre, str) or not nombre.strip():
        return jsonify(error="El nombre debe ser texto no vacío."), 400
    if not isinstance(email, str):
        return jsonify(error="El email debe ser texto."), 400
    if isinstance(edad, bool) or not isinstance(edad, int) or edad < 0:
        return jsonify(error="La edad debe ser un entero no negativo."), 400

    usuario.update(nombre=nombre.strip(), email=email.strip(), edad=edad)
    return jsonify(usuario), 200


@app.delete("/api/usuarios/<int:usuario_id>")
def eliminar_usuario(usuario_id):
    usuario = next((item for item in usuarios if item["id"] == usuario_id), None)
    if usuario is None:
        return jsonify(error="No encontrado"), 404
    usuarios.remove(usuario)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
