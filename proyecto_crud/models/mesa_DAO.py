import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.administrador import Administrador
from models.mesa import Mesa


class MesaDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_mesa(self, numero, estado, id_administrador=None):
        try:
            self._validar_administrador(id_administrador)
            mesa = Mesa(
                numero=numero,
                estado=estado,
                id_administrador=id_administrador,
            )
            mesa.validar()
            self.sesion.add(mesa)
            self.sesion.commit()
            logging.info("Mesa creada: %s", mesa.numero)
            return mesa.id_mesa
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception("No se pudo crear mesa por una referencia inválida")
            raise ValueError("El administrador seleccionado ya no existe.") from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear mesa")
            raise

    def obtener_mesas(self):
        consulta = select(Mesa).order_by(Mesa.id_mesa)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_mesa):
        return self.sesion.get(Mesa, id_mesa)

    def _validar_administrador(self, id_administrador):
        if (
            id_administrador is not None
            and self.sesion.get(Administrador, id_administrador) is None
        ):
            raise ValueError(f"No existe el administrador con ID {id_administrador}.")

    def actualizar(self, id_mesa, **datos):
        try:
            mesa = self.obtener_por_id(id_mesa)
            if mesa is None:
                self.sesion.rollback()
                return False
            self._validar_administrador(datos.get("id_administrador"))
            mesa.actualizar(**datos)
            self.sesion.commit()
            return True
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception("No se pudo actualizar mesa por referencia inválida")
            raise ValueError("El administrador seleccionado ya no existe.") from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar mesa")
            raise

    def eliminar(self, id_mesa):
        try:
            mesa = self.obtener_por_id(id_mesa)
            if mesa is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(mesa)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar mesa")
            raise
