import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.domicilio import Domicilio
from models.pedido import Pedido


class DomicilioDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _validar_pedido(self, id_pedido):
        if id_pedido is not None and self.sesion.get(Pedido, id_pedido) is None:
            raise ValueError(f"No existe el pedido con ID {id_pedido}.")

    def crear_domicilio(
        self, id_pedido=None, direccion=None, telefono=None, costo_envio=None
    ):
        try:
            if id_pedido is not None:
                id_pedido = int(id_pedido)
            self._validar_pedido(id_pedido)
            domicilio = Domicilio(
                id_pedido=id_pedido,
                direccion=direccion,
                telefono=telefono,
                costo_envio=costo_envio,
            )
            domicilio.validar()
            self.sesion.add(domicilio)
            self.sesion.commit()
            logging.info("Domicilio creado: %s", domicilio.id_domicilio)
            return domicilio.id_domicilio
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception("No se pudo crear domicilio por referencia duplicada")
            raise ValueError(
                "El pedido ya tiene un domicilio o ya no existe."
            ) from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear domicilio")
            raise

    def obtener_domicilios(self):
        consulta = select(Domicilio).order_by(Domicilio.id_domicilio)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_domicilio):
        return self.sesion.get(Domicilio, id_domicilio)

    def actualizar(self, id_domicilio, **datos):
        try:
            domicilio = self.obtener_por_id(id_domicilio)
            if domicilio is None:
                self.sesion.rollback()
                return False
            if "id_pedido" in datos and datos["id_pedido"] is not None:
                datos["id_pedido"] = int(datos["id_pedido"])
                self._validar_pedido(datos["id_pedido"])
            domicilio.actualizar(**datos)
            self.sesion.commit()
            return True
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception("No se pudo actualizar domicilio")
            raise ValueError(
                "El pedido ya tiene un domicilio o ya no existe."
            ) from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar domicilio")
            raise

    def eliminar(self, id_domicilio):
        try:
            domicilio = self.obtener_por_id(id_domicilio)
            if domicilio is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(domicilio)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar domicilio")
            raise
