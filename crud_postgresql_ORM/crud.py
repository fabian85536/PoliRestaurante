import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Usuario


class UsuarioCRUD:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre: str, email: str) -> Usuario:
        nombre, email = self._validar(nombre, email)
        usuario = Usuario(nombre=nombre, email=email)
        try:
            self.session.add(usuario)
            self.session.commit()
            return usuario
        except IntegrityError as error:
            self.session.rollback()
            raise ValueError("Ya existe un usuario con ese email.") from error
        except Exception:
            self.session.rollback()
            logging.exception("Error al crear el usuario")
            raise

    def listar(self) -> list[Usuario]:
        consulta = select(Usuario).order_by(Usuario.id)
        return list(self.session.scalars(consulta).all())

    def obtener(self, usuario_id: int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)

    def actualizar(
        self,
        usuario_id: int,
        nombre: str | None = None,
        email: str | None = None,
    ) -> bool:
        usuario = self.obtener(usuario_id)
        if usuario is None:
            return False

        nuevo_nombre, nuevo_email = self._validar(
            nombre if nombre is not None else usuario.nombre,
            email if email is not None else usuario.email,
        )
        usuario.nombre = nuevo_nombre
        usuario.email = nuevo_email
        try:
            self.session.commit()
            return True
        except IntegrityError as error:
            self.session.rollback()
            raise ValueError("Ya existe un usuario con ese email.") from error
        except Exception:
            self.session.rollback()
            logging.exception("Error al actualizar el usuario")
            raise

    def eliminar(self, usuario_id: int) -> bool:
        usuario = self.obtener(usuario_id)
        if usuario is None:
            return False

        try:
            self.session.delete(usuario)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            logging.exception("Error al eliminar el usuario")
            raise

    @staticmethod
    def _validar(nombre: str, email: str) -> tuple[str, str]:
        nombre = nombre.strip()
        email = email.strip()
        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if "@" not in email or "." not in email:
            raise ValueError("El email no es válido.")
        return nombre, email
