import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.administrador import Administrador


class AdministradorDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_administrador(self, nombre, usuario, contrasena):
        try:
            administrador = Administrador(
                nombre=nombre, usuario=usuario, contrasena=contrasena
            )
            administrador.validar()
            self.sesion.add(administrador)
            self.sesion.commit()
            logging.info("Administrador creado: %s", administrador.usuario)
            return administrador.id_administrador
        except ValueError:
            self.sesion.rollback()
            raise
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear administrador")
            raise

    def obtener_administradores(self):
        consulta = select(Administrador).order_by(Administrador.id_administrador)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_administrador):
        return self.sesion.get(Administrador, id_administrador)

    def actualizar(self, id_administrador, **datos):
        try:
            administrador = self.obtener_por_id(id_administrador)
            if administrador is None:
                self.sesion.rollback()
                return False
            administrador.actualizar(**datos)
            self.sesion.commit()
            return True
        except ValueError:
            self.sesion.rollback()
            raise
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar administrador")
            raise

    def eliminar(self, id_administrador):
        try:
            administrador = self.obtener_por_id(id_administrador)
            if administrador is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(administrador)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar administrador")
            raise
