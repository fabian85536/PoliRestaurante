import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.Producto import Producto


class ProductoDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_producto(
        self,
        nombre,
        descripcion,
        precio,
        id_categoria=None,
        id_administrador=None,
        disponible=True,
    ):
        try:
            producto = Producto(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                id_categoria=id_categoria,
                id_administrador=id_administrador,
            )
            producto.disponible = disponible
            producto.validar()
            self.sesion.add(producto)
            self.sesion.commit()
            logging.info("Producto creado: %s", producto.nombre)
            return producto.id_producto
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear producto")
            raise

    def obtener_productos(self):
        consulta = select(Producto).order_by(Producto.id_producto)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_producto):
        consulta = select(Producto).where(Producto.id_producto == id_producto)
        return self.sesion.scalar(consulta)

    def actualizar(
        self,
        id_producto,
        nombre=None,
        descripcion=None,
        precio=None,
        id_categoria=None,
        id_administrador=None,
        disponible=None,
    ):
        try:
            producto = self.obtener_por_id(id_producto)
            if producto is None:
                self.sesion.rollback()
                return False
            producto.actualizar(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                id_categoria=id_categoria,
                id_administrador=id_administrador,
                disponible=disponible,
            )
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar producto")
            raise

    def eliminar(self, id_producto):
        try:
            producto = self.obtener_por_id(id_producto)
            if producto is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(producto)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar producto")
            raise
