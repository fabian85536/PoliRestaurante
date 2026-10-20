import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.mesero import Mesero


class MeseroDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_mesero(self, nombre, usuario, contrasena):
        try:
            mesero = Mesero(nombre=nombre, usuario=usuario, contrasena=contrasena)
            mesero.validar()
            self.sesion.add(mesero)
            self.sesion.commit()
            logging.info("Mesero creado: %s", mesero.usuario)
            return mesero.id_mesero
        except ValueError:
            self.sesion.rollback()
            raise
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear mesero")
            raise

    def obtener_meseros(self):
        consulta = select(Mesero).order_by(Mesero.id_mesero)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_mesero):
        return self.sesion.get(Mesero, id_mesero)

    def actualizar(self, id_mesero, **datos):
        try:
            mesero = self.obtener_por_id(id_mesero)
            if mesero is None:
                self.sesion.rollback()
                return False
            mesero.actualizar(**datos)
            self.sesion.commit()
            return True
        except ValueError:
            self.sesion.rollback()
            raise
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar mesero")
            raise

    def eliminar(self, id_mesero):
        try:
            mesero = self.obtener_por_id(id_mesero)
            if mesero is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(mesero)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar mesero")
            raise
