from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.administrador import Administrador
from models.mesero import Mesero
from models.mesa import Mesa
from models.personal_cocina import PersonalCocina
from models.usuario import Base


class Pedido(Base):
    __tablename__ = "Pedido"

    id_pedido: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mesero: Mapped[int | None] = mapped_column(
        ForeignKey("Mesero.id_mesero"), nullable=True
    )
    id_cocina: Mapped[int | None] = mapped_column(
        ForeignKey("PersonalCocina.id_cocina"), nullable=True
    )
    id_administrador: Mapped[int | None] = mapped_column(
        ForeignKey("Administrador.id_administrador"), nullable=True
    )
    id_mesa: Mapped[int | None] = mapped_column(
        ForeignKey("Mesa.id_mesa"), nullable=True
    )
    tipo_pedido: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nombre_cliente: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metodo_pago: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_creacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_cierre: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def validar(self):
        if self.total is not None:
            self.total = int(self.total)
            if self.total < 0:
                raise ValueError("El total del pedido no puede ser negativo.")
        for campo in (
            "tipo_pedido",
            "nombre_cliente",
            "estado",
            "metodo_pago",
            "fecha_creacion",
            "fecha_cierre",
        ):
            valor = getattr(self, campo)
            if valor is not None:
                setattr(self, campo, valor.strip())

    def actualizar(self, **datos):
        for campo, valor in datos.items():
            if valor is not None:
                if campo.startswith("id_") or campo == "total":
                    valor = int(valor)
                else:
                    valor = valor.strip()
                setattr(self, campo, valor)
        self.validar()

    def to_dict(self):
        return {
            "id_pedido": self.id_pedido,
            "id_mesero": self.id_mesero,
            "id_cocina": self.id_cocina,
            "id_administrador": self.id_administrador,
            "id_mesa": self.id_mesa,
            "tipo_pedido": self.tipo_pedido,
            "nombre_cliente": self.nombre_cliente,
            "estado": self.estado,
            "total": self.total,
            "metodo_pago": self.metodo_pago,
            "fecha_creacion": self.fecha_creacion,
            "fecha_cierre": self.fecha_cierre,
        }
