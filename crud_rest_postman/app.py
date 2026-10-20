import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from flask import Flask, abort, g, jsonify, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

PROJECT_CRUD_DIR = Path(__file__).resolve().parents[1] / "proyecto_crud"
if str(PROJECT_CRUD_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_CRUD_DIR))

from database import Database
from models.administrador_DAO import AdministradorDAO
from models.mesa_DAO import MesaDAO
from models.mesero_DAO import MeseroDAO
from models.pedido_DAO import PedidoDAO
from models.personal_cocina_DAO import PersonalCocinaDAO
from models.producto_DAO import ProductoDAO
from models.usuario import Usuario
from models.usuario_DAO import UsuarioDAO


@dataclass(frozen=True)
class Resource:
    dao_factory: Callable[[Any], Any]
    list_records: Callable[[Any], list]
    find_record: Callable[[Any, int], Any]
    serialize: Callable[[Any], dict]
    create: Callable[[Any, dict], int]
    update: Callable[[Any, int, dict], bool]
    delete: Callable[[Any, int], bool]


def _object_payload() -> dict:
    payload = request.get_json()
    if not isinstance(payload, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON.")
    return payload


def _validate_fields(
    payload: dict, allowed: set[str], required: set[str] | None = None
) -> None:
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError("Campos no válidos: " + ", ".join(sorted(unknown)))
    missing = (required or set()) - set(payload)
    if missing:
        raise ValueError("Faltan campos obligatorios: " + ", ".join(sorted(missing)))


def _string(payload: dict, field: str, *, required: bool = False) -> str | None:
    value = payload.get(field)
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError(f"El campo '{field}' debe ser texto no vacío.")
    return value


def _integer(
    value: Any, field: str, *, nullable: bool = False
) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool):
        raise ValueError(f"El campo '{field}' debe ser un número entero.")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value)
    raise ValueError(f"El campo '{field}' debe ser un número entero.")


def _required_fields(
    payload: dict, allowed: set[str], required: set[str] | None = None
) -> None:
    _validate_fields(payload, allowed, required)


def _user_to_dict(user: Usuario) -> dict:
    return {"id": user.id, "nombre": user.nombre, "email": user.email}


def _create_user(dao: UsuarioDAO, payload: dict) -> int:
    fields = {"nombre", "email"}
    _required_fields(payload, fields, fields)
    nombre = _string(payload, "nombre", required=True)
    email = _string(payload, "email", required=True)
    return dao.crear_usuario(nombre, email)


def _update_user(dao: UsuarioDAO, user_id: int, payload: dict) -> bool:
    _required_fields(payload, {"nombre"}, {"nombre"})
    nombre = _string(payload, "nombre", required=True)
    user = dao.sesion.get(Usuario, user_id)
    if user is None:
        return False
    return dao.actualizar(user.email, nombre)


def _delete_user(dao: UsuarioDAO, user_id: int) -> bool:
    user = dao.sesion.get(Usuario, user_id)
    return user is not None and dao.eliminar(user.email)


def _create_product(dao: ProductoDAO, payload: dict) -> int:
    fields = {
        "nombre",
        "descripcion",
        "precio",
        "id_categoria",
        "id_administrador",
        "disponible",
    }
    _required_fields(payload, fields, {"nombre", "precio"})
    nombre = _string(payload, "nombre", required=True)
    descripcion = _string(payload, "descripcion") or ""
    precio = _integer(payload["precio"], "precio")
    id_categoria = _integer(
        payload.get("id_categoria"), "id_categoria", nullable=True
    )
    id_administrador = _integer(
        payload.get("id_administrador"), "id_administrador", nullable=True
    )
    disponible = payload.get("disponible", True)
    if not isinstance(disponible, bool):
        raise ValueError("El campo 'disponible' debe ser verdadero o falso.")
    return dao.crear_producto(
        nombre,
        descripcion,
        precio,
        id_categoria,
        id_administrador,
        disponible,
    )


def _update_product(dao: ProductoDAO, product_id: int, payload: dict) -> bool:
    fields = {
        "nombre",
        "descripcion",
        "precio",
        "id_categoria",
        "id_administrador",
        "disponible",
    }
    _required_fields(payload, fields)
    if not payload:
        raise ValueError("Incluye al menos un campo para actualizar.")
    data = dict(payload)
    for field in ("nombre", "descripcion"):
        if field in data:
            data[field] = _string(data, field)
    for field in ("precio", "id_categoria", "id_administrador"):
        if field in data:
            data[field] = _integer(data[field], field, nullable=True)
    if "disponible" in data and not isinstance(data["disponible"], bool):
        raise ValueError("El campo 'disponible' debe ser verdadero o falso.")
    return dao.actualizar(product_id, **data)


def _staff_resource(dao_factory: Callable, id_field: str) -> Resource:
    def create(dao, payload):
        fields = {"nombre", "usuario", "contrasena"}
        _required_fields(payload, fields, fields)
        data = {
            field: _string(payload, field, required=True)
            for field in fields
        }
        if id_field == "id_mesero":
            return dao.crear_mesero(**data)
        if id_field == "id_administrador":
            return dao.crear_administrador(**data)
        return dao.crear_personal_cocina(**data)

    def update(dao, record_id, payload):
        fields = {"nombre", "usuario", "contrasena"}
        _required_fields(payload, fields)
        if not payload:
            raise ValueError("Incluye al menos un campo para actualizar.")
        data = {
            field: _string(payload, field, required=True)
            for field in payload
        }
        return dao.actualizar(record_id, **data)

    def serialize(record):
        return record.to_dict()

    if id_field == "id_mesero":
        list_records = lambda dao: dao.obtener_meseros()
        find_record = lambda dao, record_id: dao.obtener_por_id(record_id)
        delete = lambda dao, record_id: dao.eliminar(record_id)
    elif id_field == "id_administrador":
        list_records = lambda dao: dao.obtener_administradores()
        find_record = lambda dao, record_id: dao.obtener_por_id(record_id)
        delete = lambda dao, record_id: dao.eliminar(record_id)
    else:
        list_records = lambda dao: dao.obtener_personal_cocina()
        find_record = lambda dao, record_id: dao.obtener_por_id(record_id)
        delete = lambda dao, record_id: dao.eliminar(record_id)

    return Resource(
        dao_factory=dao_factory,
        list_records=list_records,
        find_record=find_record,
        serialize=serialize,
        create=create,
        update=update,
        delete=delete,
    )


def _create_table(dao: MesaDAO, payload: dict) -> int:
    fields = {"numero", "estado", "id_administrador"}
    _required_fields(payload, fields, {"numero", "estado"})
    numero = _integer(payload["numero"], "numero")
    estado = _string(payload, "estado", required=True)
    id_administrador = _integer(
        payload.get("id_administrador"), "id_administrador", nullable=True
    )
    return dao.crear_mesa(numero, estado, id_administrador)


def _update_table(dao: MesaDAO, table_id: int, payload: dict) -> bool:
    fields = {"numero", "estado", "id_administrador"}
    _required_fields(payload, fields)
    if not payload:
        raise ValueError("Incluye al menos un campo para actualizar.")
    data = dict(payload)
    if "numero" in data:
        data["numero"] = _integer(data["numero"], "numero")
    if "estado" in data:
        data["estado"] = _string(data, "estado", required=True)
    if "id_administrador" in data:
        data["id_administrador"] = _integer(
            data["id_administrador"], "id_administrador", nullable=True
        )
    return dao.actualizar(table_id, **data)


def _create_order(dao: PedidoDAO, payload: dict) -> int:
    fields = dao.CAMPOS
    _required_fields(payload, fields)
    data = dict(payload)
    for field in fields:
        if field.startswith("id_") or field == "total":
            if field in data:
                data[field] = _integer(data[field], field, nullable=True)
        elif field in data:
            data[field] = _string(data, field)
    return dao.crear_pedido(**data)


def _update_order(dao: PedidoDAO, order_id: int, payload: dict) -> bool:
    fields = dao.CAMPOS
    _required_fields(payload, fields)
    if not payload:
        raise ValueError("Incluye al menos un campo para actualizar.")
    data = dict(payload)
    for field in fields:
        if field.startswith("id_") or field == "total":
            if field in data:
                data[field] = _integer(data[field], field, nullable=True)
        elif field in data:
            data[field] = _string(data, field)
    return dao.actualizar(order_id, **data)


def create_app(database_factory: Callable[[], Any] = Database) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE_FACTORY"] = database_factory

    resources = {
        "usuarios": Resource(
            dao_factory=UsuarioDAO,
            list_records=lambda dao: dao.obtener_usuarios(),
            find_record=lambda dao, record_id: dao.sesion.get(Usuario, record_id),
            serialize=_user_to_dict,
            create=_create_user,
            update=_update_user,
            delete=_delete_user,
        ),
        "productos": Resource(
            dao_factory=ProductoDAO,
            list_records=lambda dao: dao.obtener_productos(),
            find_record=lambda dao, record_id: dao.obtener_por_id(record_id),
            serialize=lambda record: record.to_dict(),
            create=_create_product,
            update=_update_product,
            delete=lambda dao, record_id: dao.eliminar(record_id),
        ),
        "meseros": _staff_resource(MeseroDAO, "id_mesero"),
        "administradores": _staff_resource(
            AdministradorDAO, "id_administrador"
        ),
        "personal_cocina": _staff_resource(PersonalCocinaDAO, "id_cocina"),
        "mesas": Resource(
            dao_factory=MesaDAO,
            list_records=lambda dao: dao.obtener_mesas(),
            find_record=lambda dao, record_id: dao.obtener_por_id(record_id),
            serialize=lambda record: record.to_dict(),
            create=_create_table,
            update=_update_table,
            delete=lambda dao, record_id: dao.eliminar(record_id),
        ),
        "pedidos": Resource(
            dao_factory=PedidoDAO,
            list_records=lambda dao: dao.obtener_pedidos(),
            find_record=lambda dao, record_id: dao.obtener_por_id(record_id),
            serialize=lambda record: record.to_dict(),
            create=_create_order,
            update=_update_order,
            delete=lambda dao, record_id: dao.eliminar(record_id),
        ),
    }

    @app.before_request
    def open_database():
        if request.path == "/health":
            return None
        database = app.config["DATABASE_FACTORY"]()
        try:
            database.conectar()
        except ValueError as error:
            logging.error("Configuración inválida de la base de datos: %s", error)
            return jsonify(error="No se pudo configurar la conexión a la base de datos."), 500
        g.database = database
        return None

    @app.teardown_request
    def close_database(_error):
        database = getattr(g, "database", None)
        if database is not None:
            database.desconectar()

    @app.errorhandler(ValueError)
    def handle_bad_input(error):
        return jsonify(error=str(error)), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        logging.error("Error de base de datos en la API: %s", error)
        return jsonify(error="Error al procesar la operación en la base de datos."), 500

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/api/<entity>", methods=["GET", "POST"])
    def collection(entity):
        resource = resources.get(entity)
        if resource is None:
            abort(404, description="Recurso no encontrado.")
        dao = resource.dao_factory(g.database.sesion)
        if request.method == "GET":
            records = resource.list_records(dao)
            return jsonify([resource.serialize(record) for record in records])

        record_id = resource.create(dao, _object_payload())
        record = resource.find_record(dao, record_id)
        response = jsonify(resource.serialize(record))
        response.status_code = 201
        response.headers["Location"] = f"/api/{entity}/{record_id}"
        return response

    @app.route(
        "/api/<entity>/<int:record_id>", methods=["GET", "PATCH", "DELETE"]
    )
    def item(entity, record_id):
        resource = resources.get(entity)
        if resource is None:
            abort(404, description="Recurso no encontrado.")
        dao = resource.dao_factory(g.database.sesion)

        if request.method == "GET":
            record = resource.find_record(dao, record_id)
            if record is None:
                return jsonify(error="Registro no encontrado."), 404
            return jsonify(resource.serialize(record))
        if request.method == "PATCH":
            if not resource.update(dao, record_id, _object_payload()):
                return jsonify(error="Registro no encontrado."), 404
            record = resource.find_record(dao, record_id)
            return jsonify(resource.serialize(record))
        if not resource.delete(dao, record_id):
            return jsonify(error="Registro no encontrado."), 404
        return "", 204

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
