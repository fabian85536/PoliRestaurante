import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.administrador import Administrador
from models.mesero import Mesero
from models.mesa import Mesa
from models.pedido import Pedido
from models.personal_cocina import PersonalCocina


class PedidoDAO:
    REFERENCIAS = {
        "id_mesero": (Mesero, "id_mesero", "mesero"),
        "id_cocina": (PersonalCocina, "id_cocina", "personal de cocina"),
        "id_administrador": (Administrador, "id_administrador", "administrador"),
        "id_mesa": (Mesa, "id_mesa", "mesa"),
    }
    CAMPOS = {
        "id_mesero",
        "id_cocina",
        "id_administrador",
        "id_mesa",
        "tipo_pedido",
        "nombre_cliente",
        "estado",
        "total",
        "metodo_pago",
        "fecha_creacion",
        "fecha_cierre",
    }

    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_pedido(self, **datos):
        try:
            self._validar_datos(datos)
            pedido = Pedido(**datos)
            pedido.validar()
            self.sesion.add(pedido)
            self.sesion.commit()
            logging.info("Pedido creado: %s", pedido.id_pedido)
            return pedido.id_pedido
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception("No se pudo crear el pedido por una referencia inválida")
            raise ValueError("Una de las referencias seleccionadas ya no existe.") from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear pedido")
            raise

    def obtener_pedidos(self):
        consulta = select(Pedido).order_by(Pedido.id_pedido)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_pedido):
        return self.sesion.get(Pedido, id_pedido)

    def _validar_datos(self, datos):
        campos_desconocidos = set(datos) - self.CAMPOS
        if campos_desconocidos:
            raise ValueError(
                "Campos de pedido no válidos: " + ", ".join(sorted(campos_desconocidos))
            )
        for campo, valor in datos.items():
            referencia = self.REFERENCIAS.get(campo)
            if referencia is None or valor is None:
                continue
            modelo, _, nombre = referencia
            if self.sesion.get(modelo, valor) is None:
                raise ValueError(f"No existe el {nombre} con ID {valor}.")

    def actualizar(self, id_pedido, **datos):
        try:
            pedido = self.obtener_por_id(id_pedido)
            if pedido is None:
                self.sesion.rollback()
                return False
            self._validar_datos(datos)
            pedido.actualizar(**datos)
            self.sesion.commit()
            return True
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception(
                "No se pudo actualizar el pedido por una referencia inválida"
            )
            raise ValueError("Una de las referencias seleccionadas ya no existe.") from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar pedido")
            raise

    def eliminar(self, id_pedido):
        try:
            pedido = self.obtener_por_id(id_pedido)
            if pedido is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(pedido)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar pedido")
            raise
