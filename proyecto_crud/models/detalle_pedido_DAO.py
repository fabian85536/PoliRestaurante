import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.detalle_pedido import DetallePedido
from models.pedido import Pedido
from models.Producto import Producto


class DetallePedidoDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _validar_referencias(self, id_pedido, id_producto):
        for modelo, valor, etiqueta in (
            (Pedido, id_pedido, "pedido"),
            (Producto, id_producto, "producto"),
        ):
            if valor is not None and self.sesion.get(modelo, valor) is None:
                raise ValueError(f"No existe el {etiqueta} con ID {valor}.")

    def crear_detalle(
        self,
        id_pedido=None,
        id_producto=None,
        cantidad=None,
        precio_unitario=None,
        notas=None,
    ):
        try:
            detalle_id = self.agregar_detalle(
                id_pedido=id_pedido,
                id_producto=id_producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                notas=notas,
            )
            self.sesion.commit()
            logging.info("Detalle de pedido creado: %s", detalle_id)
            return detalle_id
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception("No se pudo crear detalle de pedido")
            raise ValueError(
                "El pedido o producto seleccionado ya no existe."
            ) from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear detalle de pedido")
            raise

    def agregar_detalle(
        self,
        id_pedido=None,
        id_producto=None,
        cantidad=None,
        precio_unitario=None,
        notas=None,
    ):
        if id_pedido is not None:
            id_pedido = int(id_pedido)
        if id_producto is not None:
            id_producto = int(id_producto)
        self._validar_referencias(id_pedido, id_producto)
        detalle = DetallePedido(
            id_pedido=id_pedido,
            id_producto=id_producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            notas=notas,
        )
        detalle.validar()
        self.sesion.add(detalle)
        self.sesion.flush()
        return detalle.id_detalle

    def obtener_detalles(self):
        consulta = select(DetallePedido).order_by(DetallePedido.id_detalle)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_detalle):
        return self.sesion.get(DetallePedido, id_detalle)

    def actualizar(self, id_detalle, **datos):
        try:
            detalle = self.obtener_por_id(id_detalle)
            if detalle is None:
                self.sesion.rollback()
                return False
            referencias = {
                campo: int(datos[campo]) if datos[campo] is not None else None
                for campo in ("id_pedido", "id_producto")
                if campo in datos
            }
            self._validar_referencias(
                referencias.get("id_pedido", detalle.id_pedido),
                referencias.get("id_producto", detalle.id_producto),
            )
            detalle.actualizar(**datos)
            self.sesion.commit()
            return True
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.exception("No se pudo actualizar detalle de pedido")
            raise ValueError(
                "El pedido o producto seleccionado ya no existe."
            ) from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar detalle de pedido")
            raise

    def eliminar(self, id_detalle):
        try:
            detalle = self.obtener_por_id(id_detalle)
            if detalle is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(detalle)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar detalle de pedido")
            raise
