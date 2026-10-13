
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.usuario import Base


class Producto(Base):
    __tablename__ = "Producto"

    id_producto: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    precio: Mapped[int] = mapped_column(Integer, nullable=False)
    id_categoria: Mapped[int | None] = mapped_column(Integer, nullable=True)
    id_administrador: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disponibilidad: Mapped[str] = mapped_column(
        String(255), nullable=False, default="Disponible"
    )

    @property
    def id(self):
        return self.id_producto

    @property
    def disponible(self):
        return self.disponibilidad.strip().lower() in {
            "disponible",
            "si",
            "sí",
            "true",
            "1",
        }

    @disponible.setter
    def disponible(self, valor):
        self.disponibilidad = "Disponible" if valor else "No disponible"

    def validar(self):
        self.nombre = self.nombre.strip()
        self.descripcion = (self.descripcion or "").strip()
        self.precio = int(self.precio)
        if not self.nombre:
            raise ValueError("El nombre del producto es obligatorio.")

        if self.precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")

    def actualizar(
        self,
        nombre=None,
        descripcion=None,
        precio=None,
        id_categoria=None,
        id_administrador=None,
        disponible=None,
    ):
        if nombre is not None:
            self.nombre = nombre.strip()

        if descripcion is not None:
            self.descripcion = descripcion.strip()

        if precio is not None:
            self.precio = int(precio)

        if id_categoria is not None:
            self.id_categoria = int(id_categoria)

        if id_administrador is not None:
            self.id_administrador = int(id_administrador)

        if disponible is not None:
            self.disponible = disponible

        self.validar()

    def to_dict(self):
        return {
            "id": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "id_categoria": self.id_categoria,
            "id_administrador": self.id_administrador,
            "disponible": self.disponible
        }
