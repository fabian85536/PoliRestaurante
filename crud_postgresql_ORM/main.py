import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from crud import UsuarioCRUD
from database import crear_engine
from models import Base


def _leer_id() -> int:
    usuario_id = int(input("ID del usuario: "))
    if usuario_id < 1:
        raise ValueError("El ID debe ser un entero positivo.")
    return usuario_id


def main() -> None:
    engine = crear_engine()
    try:
        Base.metadata.create_all(engine)
        with Session(engine, expire_on_commit=False) as session:
            crud = UsuarioCRUD(session)
            while True:
                print(
                    "\n=== CRUD de usuarios (PostgreSQL + SQLAlchemy ORM) ===\n"
                    "1. Crear usuario\n"
                    "2. Listar usuarios\n"
                    "3. Buscar usuario por ID\n"
                    "4. Actualizar usuario\n"
                    "5. Eliminar usuario\n"
                    "0. Salir"
                )
                opcion = input("Opción: ").strip()
                try:
                    if opcion == "1":
                        usuario = crud.crear(
                            input("Nombre: "),
                            input("Email: "),
                        )
                        print(f"Usuario creado con ID {usuario.id}.")
                    elif opcion == "2":
                        for usuario in crud.listar():
                            print(f"{usuario.id}: {usuario.nombre} | {usuario.email}")
                    elif opcion == "3":
                        usuario = crud.obtener(_leer_id())
                        if usuario is None:
                            print("No se encontró el usuario.")
                        else:
                            print(f"{usuario.id}: {usuario.nombre} | {usuario.email}")
                    elif opcion == "4":
                        usuario_id = _leer_id()
                        nombre = input("Nuevo nombre: ")
                        email = input("Nuevo email: ")
                        if crud.actualizar(usuario_id, nombre, email):
                            print("Usuario actualizado.")
                        else:
                            print("No se encontró el usuario.")
                    elif opcion == "5":
                        if crud.eliminar(_leer_id()):
                            print("Usuario eliminado.")
                        else:
                            print("No se encontró el usuario.")
                    elif opcion == "0":
                        break
                    else:
                        print("Opción no válida.")
                except ValueError as error:
                    print(f"No se pudo completar la operación: {error}")
    except SQLAlchemyError:
        logging.exception("Error al conectar o trabajar con PostgreSQL")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
