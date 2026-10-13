import logging

#ORM
#usa la sesión para crear, buscar, actualizar y eliminar usuarios.

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.usuario import Usuario
from validation import validar_email


class UsuarioDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_usuario(self, nombre, email):
        if not validar_email(email):
            raise ValueError("Email inválido")

        try:
            usuario = Usuario(nombre=nombre, email=email)
            self.sesion.add(usuario)
            self.sesion.commit()
            logging.info("Usuario creado: %s", email)
            return usuario.id
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear usuario")
            raise

    def obtener_usuarios(self):
        consulta = select(Usuario).order_by(Usuario.id)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_email(self, email):
        consulta = select(Usuario).where(Usuario.email == email)
        return self.sesion.scalar(consulta)

    def actualizar(self, email, nuevo_nombre):
        try:
            usuario = self.obtener_por_email(email)
            if usuario is None:
                self.sesion.rollback()
                return False
            usuario.nombre = nuevo_nombre
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar usuario")
            raise

    def eliminar(self, email):
        try:
            usuario = self.obtener_por_email(email)
            if usuario is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(usuario)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar usuario")
            raise
