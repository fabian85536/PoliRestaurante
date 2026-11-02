from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.pedido import Pedido
from models.usuario import Base


class Domicilio(Base):
    __tablename__ = "Domicilio"

    id_domicilio: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_pedido: Mapped[int | None] = mapped_column(
        ForeignKey("Pedido.id_pedido"), unique=True, nullable=True
    )
    direccion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(255), nullable=True)
    costo_envio: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def validar(self):
        if self.direccion is not None:
            self.direccion = self.direccion.strip()
        if self.telefono is not None:
            self.telefono = self.telefono.strip()
        if self.costo_envio is not None:
            self.costo_envio = int(self.costo_envio)
            if self.costo_envio < 0:
                raise ValueError("El costo de envío no puede ser negativo.")

    def actualizar(self, **datos):
        for campo, valor in datos.items():
            if valor is not None:
                if campo in {"id_pedido", "costo_envio"}:
                    valor = int(valor)
                else:
                    valor = valor.strip()
                setattr(self, campo, valor)
        self.validar()

    def to_dict(self):
        return {
            "id_domicilio": self.id_domicilio,
            "id_pedido": self.id_pedido,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "costo_envio": self.costo_envio,
        }
