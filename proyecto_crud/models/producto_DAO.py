import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.Producto import Administrador, Categoria, Producto


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
            self._validar_referencias(id_categoria, id_administrador)
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
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.error("No se pudo crear el producto: referencia inválida")
            raise ValueError(
                "La categoría o el administrador ya no existen. "
                "Selecciona un ID vigente."
            ) from error
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear producto")
            raise

    def obtener_productos(self):
        consulta = select(Producto).order_by(Producto.id_producto)
        return list(self.sesion.scalars(consulta).all())

    def obtener_categorias(self):
        consulta = select(Categoria).order_by(Categoria.id_categoria)
        return list(self.sesion.scalars(consulta).all())

    def obtener_administradores(self):
        consulta = select(Administrador).order_by(Administrador.id_administrador)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_producto):
        consulta = select(Producto).where(Producto.id_producto == id_producto)
        return self.sesion.scalar(consulta)

    def _validar_referencias(self, id_categoria, id_administrador):
        if (
            id_categoria is not None
            and self.sesion.get(Categoria, id_categoria) is None
        ):
            raise ValueError(
                f"No existe la categoría con ID {id_categoria}. "
                "Elige una categoría registrada o deja el campo vacío."
            )
        if (
            id_administrador is not None
            and self.sesion.get(Administrador, id_administrador) is None
        ):
            raise ValueError(
                f"No existe el administrador con ID {id_administrador}. "
                "Elige un administrador registrado o deja el campo vacío."
            )

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
            self._validar_referencias(id_categoria, id_administrador)
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
        except ValueError:
            self.sesion.rollback()
            raise
        except IntegrityError as error:
            self.sesion.rollback()
            logging.error("No se pudo actualizar el producto: referencia inválida")
            raise ValueError(
                "La categoría o el administrador ya no existen. "
                "Selecciona un ID vigente."
            ) from error
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
